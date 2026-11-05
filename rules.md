Rules for the books

I want the computer to help get the books loaded. But I also want to know what it changed. Leave the CSV files alone. Keep the original values, file name, record number and supplier book_id in the history. Store ISBNs as text. Use the checks in data-validation.md. Passing those checks doesn't prove the number belongs to that book.

Check both ISBN fields. If one works, use it and warn about the other one if it is bad or missing. If both work but mean different ISBNs, reject the row. I don't want the program picking which one to believe.

To do with each problem:

- A valid ISBN is fine. For matching, convert ISBN-10 to its equivalent 978 ISBN-13 with the new check digit. Leave a valid 979 ISBN alone.
-Remove spaces and ordinary hyphens, and change lowercase x to X. If it passes after that, load it with a repair warning. If it still fails, the field is unusable.
- For a plain short value of 2 to 9 characters, containing digits and possibly a final X, add leading zeros to make an ISBN-10. Only use it if it passes. Load with a warning that we assumed zeros were missing. This is a guess I am allowing for these files. Never pad to 13 digits.
- Expand scientific notation using exact decimal arithmetic. If the whole-number result passes, load with a repair warning. Earlier rounding might still have lost something. If it fails, don't use that field.
- For decimals, remove the decimal part only if it is all zeros. Test what remains. If valid, load with a repair warning. Otherwise it is unusable. Don't pad numbers from scientific or decimal notation or round fractions.
- Wrong length, bad checksum, invalid letters or an invalid ISBN prefix make a field unusable. Don't cut off digits, replace letters or change the last digit to make it pass. We don't know which part was wrong.
- Blank means missing, including a field containing only spaces. Warn about it. Don't invent a number.
-A valid ISBN in the wrong column is still usable. Load with a column warning. A 13-digit number in isbn doesn't need shortening.

Check blanks first. Recognize numeric notation before removing hyphens, so an exponent minus sign stays intact. For ordinary values, clean spaces, hyphens and lowercase x, validate, then try the short ISBN-10 rule if needed. A leading sign on a plain identifier is invalid. Record all warnings. Formatting repairs keep the information already there. Adding zeros assumes something, and scientific notation might already be rounded. A passing checksum doesn't make those assumptions certain.

Every row needs a title, authors and a positive digits-only supplier book_id. Missing or invalid required fields mean reject. Treat IDs like 001 and 1 as the same ID. Keep authors as one text field for now.

If neither ISBN works, still load with a warning if those required fields are present. Store a null ISBN and keep the bad values in the history. So an unusable ISBN field alone doesn't reject the whole row. Conflicting usable ISBNs do.

The same book means the same catalog edition, not another physical copy. Match by usable ISBN-13 first, or by supplier Goodbooks plus book_id when there is no usable ISBN. Keep supplier IDs linked to the entry even when ISBN was used. Don't merge on title alone. Different IDs without ISBNs stay separate; warn about a possible duplicate if title and authors match.

For title and author comparisons, ignore case, trim the ends and collapse repeated whitespace. Punctuation, accents and author order still count. If an existing match has different title or authors, reject the incoming row for review. Keep the old display spelling when only case or spacing changed.


Read files in the order given and rows in file order. Check them every run. An identical delivery should be counted as unchanged, without adding another book. For other columns, trim outer whitespace and keep values as text. A changed nonblank value replaces the old one; a blank never erases it. Record old and new values. Supplier IDs are links, not values to overwrite. Rejected rows change nothing. Count accepted rows as inserted, updated or unchanged. Adding an ISBN or supplier link counts as an update.

The morning report should tell me when it ran, which files it read in order, their hashes, and whether it finished. Show rows read, inserted, updated, unchanged and rejected for each file and overall. The last four must add up to rows read. Show book counts before and after, plus rows with warnings and repairs. Explain that those extra counts overlap.

For every warning or rejection, show file, row, supplier ID, title, raw ISBNs, any interpreted values, reason and action. Show old and new values for updates. Tell me what to do next, like ask the supplier to confirm an ISBN or fill in missing information. Keep every run in the history. If a file can't be read, has broken CSV structure or is missing required columns, stop before committing any catalog changes and report the failure clearly.

A few decisions so I don't leave the program guessing

If a supplier ID already has another ISBN, reject the new row. Also reject if its ID and ISBN point to different entries. A new ID can link to an existing ISBN when title and authors agree. Add a later ISBN to a book without one only when title and authors agree and that ISBN isn't used elsewhere. Never erase a good ISBN because a later delivery has a blank or bad one.

Only book_id, title, authors, isbn and isbn13 are required headers. Store extra columns as text too. Read UTF-8 CSV, allowing a UTF-8 byte-order mark. Ignore completely empty lines. Duplicate headers, wrong field counts, unreadable files and broken CSV stop the whole run. Roll back all catalog changes from all files in that run. Count already-read rows as rejected because the run failed; report where reading stopped. Don't claim unread rows were checked.

Loaded means newly inserted. Updated is separate. Skipped means already there and unchanged. Rows not loaded means skipped and rejected; the report should also show updates and warnings. Save the full original row in the history even when it loaded normally.

Use a simple books table, supplier-ID links, and run history. Keep a JSON array of runs, adding to it without losing earlier entries. Stop if the existing JSON log can't be read. Keep a copy of each run in SQLite so a failed JSON save can be recovered on the next run. Don't run two imports at once. Timestamps and run history will change, but the same input against the same catalog must make the same decisions.

Put books.db and ingestion-log.json beside ingest.py. Run it with py ingest.py books.csv, or give several CSV paths in the order wanted. Use a plain report with expandable row details and a button to open the JSON file. No server, AI, internet or extra Python packages. Test in temporary folders first so I can do my own assignment runs.
These examples assume a new valid supplier ID, title and authors, with no database conflict. Blank means empty. Every repair, missing field or unusable field gets a warning, even when the table just says load. An identical accepted row on the next run should be unchanged.

| isbn | isbn13 | What happens |
|---|---|---|
| 0439139600 | 9780439139601 | Load. Both agree, no ISBN warning. |
| 043965548X | blank | Load. Final X is allowed; warn about the blank. |
| 031200009x | 9780312000097 | Change x to X and load. |
| 0-450-19827-8 | 9780450198274 | Remove hyphens and load. |
| ` 162 001 4750 ` | 9781620014752 | Remove spaces and load. |
| 439023483 | blank | Assume leading zero: 0439023483. Load and warn. |
| 439554934 | 9.78043955493e+12 | Pad the first; expand the second to 9780439554930. They agree. Load. |
| 439023483 | 9.78043902348e+12 | Padded ISBN-10 passes, expanded ISBN-13 fails. Load using ISBN-10. |
| blank | 9.78043902348e+12 | Expansion fails. Load without ISBN using supplier ID. |
| blank | 76783609419.0 | Still invalid without .0. Load without ISBN. |
| blank | 9780439139601.0 | Remove .0. It passes, so load. |
| 04390A3483 | blank | Don't guess what A means. Load without ISBN. |
| 15287463097 | blank | Wrong length. Load without ISBN. |
| 1854433017 | blank | Bad checksum. Load without ISBN. |
| blank | blank | Load without ISBN and warn. |
| 1555550126 | 9781555550134 | Reject. Both pass but disagree. |
| 9781982147600 | blank | Load; warn that ISBN-13 was in the isbn column. |
| blank | 9798351220413 | Load the valid 979 ISBN. Don't invent an ISBN-10. |
