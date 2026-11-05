# Week 3 Assignment

This is my Module 3 assignment for MSAI-5523.

## How to run this on my computer

1. Open the Windows Start menu, type **PowerShell**, and open **Windows PowerShell**. Administrator mode is not needed.
2. Go to the assignment folder by copying this command into the terminal and pressing Enter:

```powershell
cd "C:\Users\Admin\workspace\language-of-computation\week3-assignment"
```

3. Run the first book file:

```powershell
py ingest.py books.csv
```

Wait for the results before entering another command. This creates or updates `books.db` and adds a run to `ingestion-log.json`. The CSV stays unchanged. The first import has already been run, so running it again checks the file again without adding duplicate books.

To check the same file a second time, use the same command:

```powershell
py ingest.py books.csv
```

To import the second delivery:

```powershell
py ingest.py books-batch2.csv
```

4. Open the report in the default browser:

```powershell
Start-Process .\report.html
```

In the report, click **Open ingestion-log.json**. Select this file:

```text
C:\Users\Admin\workspace\language-of-computation\week3-assignment\ingestion-log.json
```

The newest run appears first. Expand a row to see its reason, warnings, repairs, and changes. After another import, select the log again to see the latest results. No server or internet connection is needed.

You can also open File Explorer, go to the assignment folder, and double-click `report.html`.
