# Comparing the three sets of rules

M = my saved rules.md. A = the first student's paste, headed “Rules for ingesting books.” B = the second student's paste, beginning “The code cleans each value first.” This compares the original three documents, not the combined list from our chat. No rules or code were changed.

A says its later “Answers to Claude's questions” override earlier tables, so I use those answers where they differ. B's numbered clarifications add detail to its earlier paragraphs. “Not stated” means the document does not settle that decision. It does not mean permission to do something.

With three documents, the agreement column names which ones agree. Where a rule leaves more than one outcome possible, I say so instead of choosing an outcome for the student. Agreement here is about the stated decision, not whether one design is better.

## ISBN decisions

| Decision | M: mine | A: first student | B: second student | Agreement |
|---|---|---|---|---|
| ISBN validation | Check length, characters, prefix and checksum, using data-validation.md. | Check ISBN structure and checksum. | Check length, characters, prefix and checksum. | All agree on the basic tests. |
| ISBN-10 ending in X | Valid when its checksum passes. | Allows X as the check digit. | Allows uppercase X at the end. | All agree. |
| 9790 prefix | Referenced diagnosis excludes it as a music prefix. | Describes 978 and 979, without this exception. | Describes 978 and 979, without this exception. | Only M explicitly includes the exception. |
| Already-valid values | Use them; canonicalize ISBN-10 for matching. | Load; calculate a missing equivalent when possible. | Load; calculate a missing equivalent when possible. | All accept; representation and missing-field handling differ. |
| Spaces, hyphens, lowercase x | Clean and test. Record individual repairs and warnings. Failure makes the field unusable, not necessarily the row. | Clean and test; reject when it still fails. Count repairs. | Clean and test; reject when it still fails. Count repairs. | A and B agree on rejecting failed cleanup; M differs. |
| Short plain ISBN-10 | Pad 2–9-character digit strings, allowing final X; use only if valid. Warn that zeros were assumed. | Pad with zeros, never a 1; keep only if checksum passes, otherwise reject. | Pad values shorter than 10; keep only if checksum passes, otherwise reject. Illegal characters have priority. | All allow padding; limits, warnings and failure outcomes differ. |
| Wrong checksum at correct length | Do not fix. Use another usable field or supplier-ID fallback with a warning. | Reject the row, in either column. | Reject the row. | A and B agree; M differs. |
| Illegal characters after cleanup | Field unusable; other field or supplier-ID fallback may save the row. | Reject the row. | Reject the row; illegal-character reason takes priority over too short. | A and B agree on outcome; M differs. Only B states reason priority. |
| Overlong isbn that is not valid ISBN-13 | Field unusable; row may still load. | Reject; cannot know which digit to remove. | Reject. | A and B agree; M differs. |
| Wrong-length numeric isbn13 / unrelated product code | Field unusable; use another ISBN or supplier ID. | If isbn is valid, leave isbn13 blank and warn; otherwise reject. | Treat as another code. With good isbn, leave isbn13 blank and warn. With blank isbn, load without ISBN if title/author identify it. | All differ in the fallback, though all can use a good isbn. |
| Scientific notation with valid isbn | Expand exactly and validate independently. Use good isbn if expansion fails. Reject if both usable values disagree. | Derive ISBN-13 from isbn; accept only if it rounds to supplied scientific value. Otherwise reject. | Same confirmation approach, explicitly at 12 significant digits. Never store the rounded number. | A and B broadly agree; M differs. Only B specifies precision. |
| Scientific notation without valid isbn | A passing exact expansion is usable with warning; otherwise supplier-ID fallback. | Blank isbn with rounded isbn13 means reject. | Blank isbn with rounded isbn13 means load without ISBN and warn, provided title/author identify it. | All three differ. |
| Decimal form | Remove only an all-zero decimal fraction, then validate; no rounding or padding of numeric conversions. | Early table says remove decimal and validate; later answer permits unusable decimal codes to stay blank with good isbn, otherwise reject. | No explicit decimal-cleaning rule. Its “another kind of code” rule supplies the fallback for numbers not looking like ISBN-13. | M and A discuss decimal cleanup; B does not explicitly authorize it. A is less precise about fractions. |
| One field blank, other valid | Use good field and warn; no requirement to fill both source fields. | Calculate missing equivalent. | Calculate missing equivalent. | A and B agree; M differs. |
| Valid 979 ISBN-13 | Keep it; do not invent ISBN-10. | Leave ISBN-10 blank. | Leave ISBN-10 blank. | All agree. |
| Valid ISBN-13 in isbn | Accept with wrong-column warning. | Move to isbn13 and calculate ISBN-10 when possible. | Move to isbn13; missing-equivalent rule then applies. | A and B agree in effect; M differs in storage/warning treatment. |
| Valid ISBN-10 in isbn13 | Accept with wrong-column warning. | Does not explicitly address this placement. | Its wrong-length isbn13 rule treats a number not looking like ISBN-13 as another code; does not explicitly rescue it as ISBN-10. | M explicitly allows it; A is silent; B's stated classification differs for numeric values. |
| Two valid ISBNs disagree | Reject. | Reject. | Reject and report both values. | All agree. |
| Conflict after moving ISBN-13 out of isbn | Reject when both usable values conflict; an unusable other field can be ignored with warning. | General disagreement rule applies; conflict with an unusable value is not fully specified. | Explicitly rejects if moved value differs from an existing isbn13 value. | Agree for valid conflicts; B's move rule is broader. |
| Both ISBNs blank | Load with null ISBN if required title, authors and supplier ID exist. | Reject, including a previously known book. | Load with empty ISBNs if title/author identify it; reject missing/placeholder identity. | M and B allow fallback but use different identities; A rejects. |
| A repair might be a guess | Explicitly admits padding assumes missing zeros; numeric notation may have lost precision. | Says a repair must give one exact answer under ISBN rules; otherwise reject. | Distinguishes checking a proposed value from choosing digits merely to pass; uncertain values are not repaired. | All discuss uncertainty, but describe acceptable evidence differently. |
| Warn for every blank or repair | Yes, with all applicable warnings. | Count repairs; list warnings, but not every repair individually. Blank equivalents can simply be repaired. | Count repairs by type; warnings are separate. Does not require a warning for every repair. | A and B differ from M's blanket warnings. |

## Same book and repeat deliveries

| Decision | M | A | B | Agreement |
|---|---|---|---|---|
| Main book identity | Same edition by canonical ISBN-13; supplier ID fallback. | ISBN, ISBN13, title, author and publication year all match after repairs. | ISBN-13 first, then ISBN-10 when ISBN-13 is absent; title/author fallback. | All differ in complete identity rules. |
| No-ISBN matching | Supplier Goodbooks plus normalized book_id. Never merge on title alone. | No usable ISBN means reject. | Match title and author, ignoring capitalization and extra spaces. | All differ. |
| One row has ISBN, another does not | Supplier link can identify it; title/author alone do not merge them. | No-ISBN incoming row is rejected. | Matching title and author make them the same book. | All differ. |
| Several title/author matches | Keep separate supplier-ID entries; warn about possible duplicates. | No matching fallback described because no-ISBN rows are rejected. | Reject ambiguous no-ISBN match. | Different approaches; only B states an explicit multiple-match rejection. |
| Required title, author, supplier ID | All required; ID must be positive digits, with 001 equal to 1. | Does not state equivalent field requirements or ID normalization. | Title/author must identify a no-ISBN row; no positive-ID requirement stated. | Only M requires and normalizes supplier ID. |
| Placeholder titles/authors | No explicit placeholder rejection. | No explicit placeholder rejection. | Reject no-ISBN row when whole field is Unknown, Untitled or Untitled Manuscript, ignoring case. | Only B. |
| Comparing title and author | Ignore case and repeated whitespace; preserve punctuation, accents and author order as significant. | Says title and author must match, but does not define text normalization. | Ignore capitalization and extra spaces. | M and B agree on case/space normalization; A is unspecified. Only M spells out the other distinctions. |
| Same ISBN, both title and author different | Reject. | Reject ISBN belonging to another book. | Reject, report both books, keep old entry. | All agree for clearly different books. |
| Same ISBN, only title or only author different | Reject. | Identity definition requires both to match, but its general changed-values rule also permits updates; this exact boundary is not settled clearly. | Treat as same book with warning. | M and B disagree; A has an unresolved boundary. |
| Publication year in identity | Not part of identity; a nonblank change can update it. | Explicitly part of identity. | Not part of stated identity; subject to nonblank update rule. | M and B align; A differs. |
| Same supplier ID, different ISBN/title/author/year | Reject conflicting ISBN or title/author; year alone can update. | Load a separate book with warning. Existing-ISBN-to-different-book rejection still also needs to be considered. | Supplier ID not described as an identity key; use ISBN/title/author rules. | Different approaches; B has no special supplier-ID rule. |
| ID points to one entry, ISBN to another | Reject. | No equivalent linked-ID rule; shared supplier IDs are allowed. | No explicit rule for supplier-ID links. | Only M specifies this conflict. |
| New supplier ID for existing ISBN | Link when title/author agree. | Supplier ID need not be unique; exact link structure not stated. | No link rule stated. | Only M explicitly specifies links. |
| Later good ISBN for existing no-ISBN book | Add if identity agrees and ISBN is unused elsewhere. | No accepted no-ISBN entries under its rules. | Title/author matching can identify same book; nonblank update rule applies. | M and B allow this in principle; A's design excludes the starting case. |
| Later blank or bad ISBN | Preserve stored good ISBN; warn if row otherwise accepted. | Both blank means reject; other ISBN errors follow A's rejection rules. | Blank never overwrites existing values, but bad ISBNs can reject under validation rules. | M and B protect stored values; acceptance decisions differ from each other and A. |
| Exact repeat, including within a file | Skip unchanged. | Skip unchanged. | Skip unchanged. | All agree. |
| Duplicate means another physical copy | No extra copy added. | No edition-count increment for exact repeat; books_count is Goodreads' edition count. | Skip unchanged; does not discuss physical copies explicitly. | All skip repeats; M and A explain count consequences. |
| Changed non-identity values | Replace nonblank incoming values; preserve old values against blanks. | Replace old with new values; no explicit blank protection. | Replace only nonblank values; preserve old against blanks. | M and B agree; A does not settle blank protection. |
| Which file is newer | Process given file order and update accordingly. | New delivery replaces changed details; file-order policy not explicit. | Latest loaded file is treated as newest, acknowledging no source dates. | M and B compatible; B explicitly states the recency assumption. |
| Check rows again on repeat runs | Explicitly every row every run. | Defines skip behavior, but does not explicitly require revalidating every row. | Requires repeat runs not to duplicate books; full revalidation is not explicit. | Only M explicitly requires rechecking every row. |

## Storage, failure handling and report

| Decision | M | A | B | Agreement |
|---|---|---|---|---|
| Stored source columns | Required five headers plus extra columns stored as text; trim outer whitespace for other values. | All 23 columns with repaired ISBNs. | All 23 columns exactly as supplied except repaired ISBN fields; later updates obey nonblank rule. | A and B require 23; M is flexible. B is most explicit about keeping other source values exact. |
| Original ISBNs and repair history | Keep complete original rows and individual repair details in history. | Original ISBNs stay in CSV, not database; repairs counted rather than individually listed. | Lists updates and warnings and repair counts; original-row retention is not specified. | M and A differ; B is silent on full original retention. |
| Preserve source files | Explicitly leave CSVs unchanged. | Says original ISBNs remain in CSV files. | Refers to correcting source rows and loading again; does not expressly require permanent source immutability. | M explicit; A preserves originals in source; B not explicit. |
| No AI or internet during ingestion | Explicit. | Explicit. | Not explicitly stated in this pasted version. | M and A agree; B silent. |
| File reading requirements | UTF-8/BOM, ignore empty lines, required headers, reject duplicate headers and wrong field counts. | Not specified. | Wrong field count makes file unreadable; other details not specified. | M and B agree on field counts; only M specifies the rest. |
| Failed run | Roll back whole run, record failure and stopping point; do not claim unread rows checked. | Error reporting requested, but rollback behavior not specified. | Roll back all changes for missing/unreadable files or a run stopping midway; log error and damaged line. | M and B agree; A silent on rollback. |
| Log retention and recovery | Append runs, preserve history, stop on unreadable log, SQLite recovery copy, one import at a time. | Does not specify these mechanisms. | Does not specify these mechanisms. | Only M. |
| Run details | Time, ordered files, hashes, completion status, catalog counts before/after. | Daily counts; no explicit hashes/time/catalog-before-after requirement. | Files, date and time. | M and B overlap; only M requires hashes and catalog counts. |
| Outcome counts | Read, inserted, updated, skipped, rejected; outcome totals must equal read. | Loaded, updated, skipped, rejected, plus rejection counts by reason. | Same reconciliation as M; explicitly say when totals fail to add up. | All require outcome counts. M and B require reconciliation; only A explicitly requires rejection totals by reason. |
| Repair and warning counts | Both counted separately; explain overlap with outcomes. | Count repairs; list warning rows. Explicit warning total not required. | Repairs and warnings counted separately; repairs by type. | Shared reporting intent, with different detail. |
| Rows listed | All originals retained; show warned/rejected rows and changes; skipped rows included as not loaded. | Rows not loaded and rows loaded with warnings. | Rejected and skipped rows listed individually under separate headings. | All cover nonloaded and warned rows; B specifies separate headings. |
| Update details | Old/new values, source location and action. | Count updates; individual old/new values not explicitly required. | Old/new values, file and line. | M and B agree; A less specific. |
| Rejection details | File, record, supplier ID, title, raw/interpreted ISBNs, reason, action and next step. | Rows not loaded and reasons. | File, line, title, value, reason, next action; show both books for conflicts. | All require reasons; M and B require more detail. |
| Suggested next action | Tell reader what to check or supply. | Not explicitly required. | Fixed sentence per reason; conflicts say to check which value/book is correct. | M and B overlap; only B fixes wording. |
| Report verdict | Completed/failed status, with rejected and warning counts. | No explicit verdict rule. | Everything loaded / some rows need attention / failed; only rejections trigger attention, not warnings. | Only B specifies this three-way verdict. |
| Report and log parity | Log history plus local expandable report selected through file button. | Says log and report list nonloaded/warning rows and count repairs. | Updates, warnings and repair counts in both JSON and HTML. | All describe reporting; only M explicitly specifies local file-opening UI here. |
| Test setup | Temporary folders before personal assignment runs. | No test environment stated. | No test environment stated. | Only M. |

## Checking M's 18 examples under all three sets

These examples supply both columns. Keep M's stated setup: new valid supplier ID, nonblank identifying title and authors, no existing database conflict, and no placeholders. “Warn” does not necessarily mean the same warning text under each set. Accepted ISBN-10 values are shown as ISBN-10 below for readability even though M uses canonical ISBN-13 for matching.

| # | isbn / isbn13 | M outcome | A outcome | B outcome | What differs? |
|---:|---|---|---|---|---|
| 1 | 0439139600 / 9780439139601 | Load, agree. | Load, agree. | Load, agree. | No material outcome difference. |
| 2 | 043965548X / blank | Load, warn about blank; canonical ISBN-13 for matching. | Load and fill equivalent ISBN-13. | Load and fill equivalent ISBN-13. | All load; missing-field storage and repair/warning reporting differ. |
| 3 | 031200009x / 9780312000097 | Uppercase X; load with repair warning. | Uppercase X; load, count repair. | Uppercase X; load, count repair. | Same acceptance; M requires repair warning. |
| 4 | 0-450-19827-8 / 9780450198274 | Remove hyphens; load with repair warning. | Remove hyphens; load, count repair. | Remove hyphens; load, count repair. | Same acceptance; warning policy differs. |
| 5 | spaced 162 001 4750 / 9781620014752 | Remove spaces; load with repair warning. | Remove spaces; load, count repair. | Remove spaces; load, count repair. | Same acceptance; warning policy differs. |
| 6 | 439023483 / blank | Pad to 0439023483; load with warnings. | Pad, calculate missing ISBN-13, load. | Pad, calculate missing ISBN-13, load. | All load; storage and warnings differ. |
| 7 | 439554934 / 9.78043955493e+12 | Pad first; exact expansion 9780439554930 passes and agrees; load with warnings. | Pad first; derived ISBN-13 agrees with rounded value; load. | Same confirmation at 12 significant digits; load. | Same resulting identity, different test and warning rules. |
| 8 | 439023483 / 9.78043902348e+12 | Expanded 9780439023480 fails; use padded ISBN-10 and warn. | Derived 9780439023481 rounds to supplied value; repair and load. | Same; store 9780439023481 and load. | All load, but M marks supplied ISBN-13 unusable; A/B repair it by confirmation. |
| 9 | blank / 9.78043902348e+12 | Load without ISBN using supplier ID. | Reject: rounded ISBN-13 has no confirming ISBN-10. | Load without ISBN using title/author and warn. | A rejects; M/B load using different identities. |
| 10 | blank / 76783609419.0 | Strip .0, still invalid; load without ISBN. | Reject: no usable ISBN. | Treat as other code; load without ISBN and warn. | A rejects; M/B load. |
| 11 | blank / 9780439139601.0 | Strip .0; load using valid ISBN-13 and warn. | Early decimal rule allows validation and loading; later answer groups decimal codes together, leaving treatment of a valid .0 value unclear. | No explicit .0 repair. Under literal “13 digits” classification, it is another code: load without ISBN. | M uses ISBN; B's literal rule does not. A needs clarification. |
| 12 | 04390A3483 / blank | Field unusable; load without ISBN. | Reject illegal character. | Reject illegal character. | M loads; A/B reject. |
| 13 | 15287463097 / blank | Field unusable; load without ISBN. | Reject wrong length. | Reject overlong isbn. | M loads; A/B reject. |
| 14 | 1854433017 / blank | Field unusable; load without ISBN. | Reject checksum failure. | Reject checksum failure. | M loads; A/B reject. |
| 15 | blank / blank | Load using supplier ID; warn. | Reject. | Load using title/author; warn. | A rejects; M/B load using different identities. |
| 16 | 1555550126 / 9781555550134 | Reject disagreement. | Reject disagreement. | Reject disagreement. | All reject. |
| 17 | 9781982147600 / blank | Use valid ISBN-13; wrong-column and blank warnings. | Move into isbn13; calculate ISBN-10; load. | Move and fill missing equivalent; load. | All load; field repair/storage differs. |
| 18 | blank / 9798351220413 | Load ISBN-13; missing-field warning. | Load; leave ISBN-10 blank. | Load; leave ISBN-10 blank. | All load; M explicitly requires blank warning. |

## Checking A's 12 numbered examples under all three sets

A's table supplies only one ISBN value, not its column, the other field, title/author or supplier ID. That matters: a wrong-prefix number in isbn13 can be treated as an unrelated code, while the same text in isbn can trigger rejection.

For a comparable result, the table below uses this explicit scenario, not a claim about omitted source data: the listed value is in isbn, isbn13 is blank, required identifying fields are present, and records are new except example 12, which repeats example 11 with the same metadata and supplier ID. Successful 13-digit values therefore also involve wrong-column handling. If values were placed in isbn13 instead, the rejection examples could have different outcomes under B.

The stated checksum outcomes in A's numbered examples were independently checked. This checks the number only, not its assignment to the book.

| # | A's example value | A's printed expectation | M under stated scenario | A under stated scenario | B under stated scenario | Difference |
|---:|---|---|---|---|---|---|
| 1 | 9770684830421 | Reject invalid prefix. | Load without ISBN using supplier ID; warn. | Reject. | Reject: overlong isbn is not valid ISBN-13. | M loads; A/B reject. If in isbn13 with blank isbn, B would instead allow no-ISBN loading. |
| 2 | 9780747532699 | Load valid ISBN. | Load; wrong-column/blank warnings. | Move, calculate ISBN-10, load. | Move, calculate ISBN-10, load. | Same acceptance, different repairs/warnings. |
| 3 | 978-04-51-52493-5 | Repair dashes. | Clean, load, warn. | Clean, move, calculate equivalent, load. | Clean, move, calculate equivalent, load. | All accept; stored fields and warning details differ. |
| 4 | 9780061120085 | Reject bad check digit. | Load without ISBN; warn. | Reject. | Reject. | M loads; A/B reject. |
| 5 | 9780141439518 | Load valid ISBN. | Load with column/blank warnings. | Move, fill equivalent, load. | Move, fill equivalent, load. | Same acceptance; storage/report differences. |
| 6 | 014062022X | Reject bad check digit. | Load without ISBN; warn. | Reject. | Reject. | M loads; A/B reject. |
| 7 | 9781408855652 | Load valid ISBN. | Load with column/blank warnings. | Move, fill equivalent, load. | Move, fill equivalent, load. | Same acceptance; storage/report differences. |
| 8 | 9780439023481 | Load valid ISBN. | Load with column/blank warnings. | Move, fill equivalent, load. | Move, fill equivalent, load. | Same acceptance; storage/report differences. |
| 9 | 9783161484100 | Load valid ISBN. | Load with column/blank warnings. | Move, fill equivalent, load. | Move, fill equivalent, load. | Same acceptance; storage/report differences. |
| 10 | 9780521825146 | Load valid ISBN. | Load with column/blank warnings. | Move, fill equivalent, load. | Move, fill equivalent, load. | Same acceptance; storage/report differences. |
| 11 | 9780743273565 | Load valid ISBN. | Load with column/blank warnings. | Move, fill equivalent, load. | Move, fill equivalent, load. | Same acceptance; storage/report differences. |
| 12 | 9780743273565 again | Skip existing book. | Skip unchanged; still validate and record applicable warnings. | Skip unchanged after repairs. | Skip unchanged after repairs. | All skip under the explicit identical-record assumption. |

A also has illustrative values in its problem tables, rather than its numbered example table. Most are already covered by M's examples above. Additional cases are:

| Additional example | M | A | B |
|---|---|---|---|
| isbn 385535144, other field blank | Padding fails checksum; load without ISBN if required fields exist. | Reject. | Reject. |
| isbn 1416913184, other field blank | Bad checksum; load without ISBN if required fields exist. | Reject. | Reject. |
| isbn13 2.94001623192e+12 | Unusable prefix; use good other ISBN or supplier fallback. | Good isbn: load with warning and blank isbn13. Blank isbn: reject. | Good isbn: load with warning and blank isbn13. Blank isbn: allow no-ISBN loading if title/author identify it. |
| book 10013, ISBN already assigned to a different book | Reject when title or authors differ. | Reject. | Reject when both title and author differ; only one differing field instead loads with warning. The book ID alone does not establish which case applies. |
| book 10001, exact duplicate row | Skip. | Skip. | Skip. |

A also compares 439139600 with 0439139600 in its later clarifications. This is the same zero-padding principle already compared above. No separate examples table was supplied for B, so there is no third table to cross-check. This document compares both available tables and does not invent missing examples or missing companion fields.

The main differences in the supplied examples are whether a damaged or missing ISBN rejects the whole row, whether rounded scientific notation is repaired from the other ISBN, and whether missing equivalent fields are filled. These are descriptions of the rules, not a ranking of them.
