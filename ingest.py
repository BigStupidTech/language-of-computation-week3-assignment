"""Load supplier CSVs using rules.md. Standard library only; no network access."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

REQUIRED = {'book_id', 'title', 'authors', 'isbn', 'isbn13'}

def valid(s):
    if re.fullmatch(r'[0-9]{9}[0-9X]', s):
        return sum((10-i)*(10 if c == 'X' else int(c)) for i,c in enumerate(s)) % 11 == 0
    return bool(re.fullmatch(r'(978|979)[0-9]{10}', s)) and not s.startswith('9790') and sum(int(c)*(1 if i%2 == 0 else 3) for i,c in enumerate(s)) % 10 == 0

def canonical(s):
    if len(s) == 13:
        return s
    base = '978' + s[:9]
    return base + str(-sum(int(c)*(1 if i%2 == 0 else 3) for i,c in enumerate(base)) % 10)

def isbn(raw):
    warnings, repairs = [], []
    s = raw.strip()
    if not s:
        return None, ['Missing ISBN'], repairs, None
    numeric = re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)', s)
    decimal = re.fullmatch(r'[0-9]+\.[0-9]+', s)
    if numeric or decimal:
        try:
            d = Decimal(s)
            if decimal and any(c != '0' for c in s.split('.')[1]):
                raise ValueError('Nonzero decimal fraction')
            if d != d.to_integral_value() or not (0 < d < Decimal('1e13')):
                raise ValueError('Not a positive whole ISBN-sized number')
            candidate = format(d, 'f').split('.')[0]
        except (InvalidOperation, ValueError) as e:
            return None, ['Unusable numeric ISBN: ' + str(e)], [], None
        if valid(candidate):
            repairs.append('Expanded numeric notation to ' + candidate)
            warnings.append('Numeric notation repaired; earlier rounding may have lost information')
            return canonical(candidate), warnings, repairs, candidate
        return None, ['Expanded numeric value fails ISBN validation'], [], candidate
    if s.startswith(('+', '-')):
        return None, ['Leading sign is invalid on a plain ISBN'], [], s
    cleaned = re.sub(r'\s|-', '', s).replace('x', 'X')
    if cleaned != raw:
        repairs.append('Removed whitespace/hyphens or uppercased x: ' + cleaned)
        warnings.append('ISBN presentation repaired')
    if valid(cleaned):
        return canonical(cleaned), warnings, repairs, cleaned
    if re.fullmatch(r'[0-9]{1,8}[0-9X]', cleaned) and len(cleaned) < 10:
        padded = cleaned.zfill(10)
        if valid(padded):
            warnings.append('Assumed missing leading zeros')
            repairs.append('Padded ISBN-10 to ' + padded)
            return canonical(padded), warnings, repairs, padded
    if len(cleaned) not in (10, 13):
        reason = 'Wrong length (or short ISBN failed zero-padding check)'
    elif not re.fullmatch(r'[0-9]{9}[0-9X]' if len(cleaned) == 10 else r'[0-9]{13}', cleaned):
        reason = 'Invalid ISBN characters'
    elif len(cleaned) == 13 and (cleaned[:3] not in ('978','979') or cleaned.startswith('9790')):
        reason = 'Invalid book ISBN prefix'
    else:
        reason = 'Bad ISBN checksum'
    return None, warnings + [reason], repairs, cleaned

def norm(s):
    return ' '.join(s.split()).casefold()

def counts():
    return dict(read=0, loaded=0, updated=0, skipped=0, rejected=0, warning_rows=0, repair_rows=0)

def save_log(path, history):
    temp = path.with_suffix('.json.tmp')
    with temp.open('w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)

def run(paths, home):
    logpath = home / 'ingestion-log.json'
    history = json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else []
    if not isinstance(history, list) or any(not isinstance(x, dict) for x in history):
        raise ValueError('Existing log must be a JSON array of run entries; no changes made')
    db = sqlite3.connect(home / 'books.db')
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY, isbn13 TEXT UNIQUE, title TEXT NOT NULL, authors TEXT NOT NULL, extras TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS supplier_ids(supplier TEXT NOT NULL, supplier_id TEXT NOT NULL, book INTEGER NOT NULL REFERENCES books(id), PRIMARY KEY(supplier,supplier_id));
    CREATE TABLE IF NOT EXISTS run_history(id INTEGER PRIMARY KEY, entry TEXT NOT NULL);
    ''')
    # Recover entries committed to SQLite if a prior JSON write failed.
    for record in db.execute('SELECT entry FROM run_history ORDER BY id'):
        old = json.loads(record[0])
        if old not in history:
            history.append(old)
    runlog = dict(when=datetime.now(timezone.utc).isoformat(), status='completed', files=[], counts=counts(), book_count_before=db.execute('SELECT count(*) FROM books').fetchone()[0])
    prepared = []
    try:
        for path in paths:
            item = dict(file=str(path.resolve()), sha256=None, counts=counts(), rows=[])
            runlog['files'].append(item)
            data = path.read_bytes()
            item['sha256'] = hashlib.sha256(data).hexdigest()
            reader = csv.reader(io.StringIO(data.decode('utf-8-sig'), newline=''), strict=True)
            header = next(reader, None)
            if not header or len(set(header)) != len(header) or not REQUIRED.issubset(header):
                raise ValueError(f'{path.name}: missing required or duplicate headers')
            rows = []
            prepared.append((item, rows))
            for number, fields in enumerate(reader, 2):
                if not fields:
                    continue
                if len(fields) != len(header):
                    raise ValueError(f'{path.name}, record {number}: wrong field count')
                rows.append((number, dict(zip(header, fields))))
                item['counts']['read'] += 1
        db.execute('BEGIN')
        for item, rows in prepared:
            for number, raw in rows:
                result = dict(record=number, supplier_id=raw['book_id'], title=raw['title'], raw=raw, interpreted={}, warnings=[], repairs=[], changes={}, outcome=None, reason='', next_action='')
                item['rows'].append(result)
                usable = []
                for col in ('isbn', 'isbn13'):
                    value, warnings, repairs, interpreted = isbn(raw[col])
                    result['interpreted'][col] = interpreted
                    result['warnings'].extend(col + ': ' + w for w in warnings)
                    result['repairs'].extend(col + ': ' + r for r in repairs)
                    if value:
                        usable.append(value)
                        if len(interpreted) != (10 if col == 'isbn' else 13):
                            result['warnings'].append(col + ': valid ISBN in wrong column')
                problems = []
                sid = raw['book_id']
                if not re.fullmatch(r'[0-9]+', sid) or not sid.strip('0'):
                    problems.append('Supplier book_id must be positive digits only')
                else:
                    sid = sid.lstrip('0')
                if not raw['title'].strip() or not raw['authors'].strip():
                    problems.append('Missing title or authors')
                if len(set(usable)) > 1:
                    problems.append('Conflicting usable ISBNs')
                chosen = usable[0] if usable else None
                byid = db.execute('SELECT b.* FROM books b JOIN supplier_ids s ON b.id=s.book WHERE s.supplier=? AND s.supplier_id=?', ('Goodbooks',sid)).fetchone()
                byisbn = db.execute('SELECT * FROM books WHERE isbn13=?', (chosen,)).fetchone() if chosen else None
                if byid and byisbn and byid['id'] != byisbn['id']:
                    problems.append('Supplier ID and ISBN point to different books')
                if byid and chosen and byid['isbn13'] and byid['isbn13'] != chosen:
                    problems.append('Supplier ID already has a different ISBN')
                match = byisbn or byid
                if match and (norm(match['title']) != norm(raw['title']) or norm(match['authors']) != norm(raw['authors'])):
                    problems.append('Title or authors differ from existing book')
                if problems:
                    result.update(outcome='rejected', reason='; '.join(problems), next_action='Confirm ISBN/edition and supplier ID with supplier; supply missing title or authors if noted.')
                else:
                    extra = {k:v.strip() for k,v in raw.items() if k not in REQUIRED}
                    if not chosen:
                        for b in db.execute('SELECT id,title,authors FROM books WHERE isbn13 IS NULL'):
                            if (not match or b['id'] != match['id']) and norm(b['title']) == norm(raw['title']) and norm(b['authors']) == norm(raw['authors']):
                                result['warnings'].append('Possible duplicate without ISBN; kept separate')
                                break
                    if match:
                        old = json.loads(match['extras'])
                        for k,v in extra.items():
                            if v and old.get(k) != v:
                                result['changes'][k] = dict(old=old.get(k), new=v)
                                old[k] = v
                        if not match['isbn13'] and chosen:
                            result['changes']['isbn13'] = dict(old=None, new=chosen)
                        if not byid:
                            db.execute('INSERT INTO supplier_ids VALUES (?,?,?)', ('Goodbooks',sid,match['id']))
                            result['changes']['supplier_link'] = dict(old=None,new=sid)
                        if result['changes']:
                            db.execute('UPDATE books SET isbn13=?,extras=? WHERE id=?', (match['isbn13'] or chosen,json.dumps(old,ensure_ascii=False),match['id']))
                        result['outcome'] = 'updated' if result['changes'] else 'skipped'
                        result['reason'] = 'Existing book updated' if result['changes'] else 'Already exists; no stored values changed'
                    else:
                        cur = db.execute('INSERT INTO books(isbn13,title,authors,extras) VALUES (?,?,?,?)', (chosen,raw['title'].strip(),raw['authors'].strip(),json.dumps(extra,ensure_ascii=False)))
                        db.execute('INSERT INTO supplier_ids VALUES (?,?,?)', ('Goodbooks',sid,cur.lastrowid))
                        result.update(outcome='loaded',reason='Inserted new catalog edition')
                    if result['warnings']:
                        result['next_action'] = 'Review noted ISBN assumptions or missing values with supplier; confirm possible duplicates if flagged.'
                item['counts'][result['outcome']] += 1
                item['counts']['warning_rows'] += bool(result['warnings'])
                item['counts']['repair_rows'] += bool(result['repairs'])
    except Exception as e:
        db.rollback()
        runlog['status'] = 'failed'
        runlog['error'] = str(e)
        for item in runlog['files']:
            item['counts'].update(loaded=0,updated=0,skipped=0,rejected=item['counts']['read'])
            available = {r['record']:r for r in item['rows']}
            for prepared_item, rows in prepared:
                if prepared_item is item:
                    for number, raw in rows:
                        available.setdefault(number, dict(record=number,supplier_id=raw['book_id'],title=raw['title'],raw=raw,interpreted={},warnings=[],repairs=[],changes={}))
            item['rows'] = list(available.values())
            for r in item['rows']:
                r.update(outcome='rejected', reason='Run failed; no catalog changes committed: '+str(e), changes={}, next_action='Correct the file error and rerun all files.')
            item['counts']['warning_rows'] = sum(bool(r['warnings']) for r in item['rows'])
            item['counts']['repair_rows'] = sum(bool(r['repairs']) for r in item['rows'])
    for item in runlog['files']:
        for key, value in item['counts'].items():
            runlog['counts'][key] += value
    runlog['book_count_after'] = db.execute('SELECT count(*) FROM books').fetchone()[0]
    db.execute('INSERT INTO run_history(entry) VALUES (?)', (json.dumps(runlog,ensure_ascii=False),))
    db.commit()
    db.close()
    history.append(runlog)
    save_log(logpath, history)
    print(json.dumps({k:v for k,v in runlog.items() if k != 'files'}, indent=2))
    return 0 if runlog['status'] == 'completed' else 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path, help='CSV files, processed in supplied order')
    args = parser.parse_args()
    try:
        sys.exit(run(args.files, Path(__file__).resolve().parent))
    except Exception as exc:
        print('Stopped: '+str(exc), file=sys.stderr)
        sys.exit(1)
