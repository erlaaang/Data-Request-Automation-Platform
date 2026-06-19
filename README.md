# BRI Insurance - Automated Report Distribution Bot

## Overview

Automated Report Distribution Bot is a Python-based solution developed by the Data Management Department to automate report requests received through email.

The solution monitors incoming emails, identifies report requests based on predefined Request IDs, executes corresponding SQL Server stored procedures, generates Excel reports, secures the files using password-protected ZIP archives, uploads them to OneDrive, and automatically replies to the original email thread with a download link.

This automation significantly reduces manual effort in report generation and distribution while improving consistency, traceability, and response time.

---

## Key Features

* Automated email request processing
* Request ID based report mapping
* SQL Server stored procedure execution
* Excel report generation
* Password-protected ZIP archive creation
* OneDrive upload integration
* Organization-wide share link generation
* Automatic Reply-All email response
* Processing audit log
* Duplicate request prevention
* Scheduled execution through Windows Task Scheduler

---

## Business Process

### Current Process

1. User sends report request email.
2. Data Management team receives request.
3. Staff manually executes SQL query or stored procedure.
4. Staff exports result to Excel.
5. Staff compresses file into ZIP.
6. Staff uploads file to OneDrive.
7. Staff replies to requester.
8. Staff manually tracks completed requests.

### Automated Process

1. User sends report request email.
2. Bot detects request email.
3. Bot identifies Request ID.
4. Bot executes corresponding stored procedure.
5. Bot generates Excel report.
6. Bot creates password-protected ZIP archive.
7. Bot uploads file to OneDrive.
8. Bot generates share link.
9. Bot replies to original email thread.
10. Bot records processing history.

---

## System Architecture

Requester Email
↓
Microsoft Graph API
↓
Report Automation Bot (Python)
↓
SQL Server Stored Procedure
↓
Excel Generation
↓
ZIP Encryption
↓
OneDrive Upload
↓
Share Link Creation
↓
Reply-All Email
↓
EmailAutomationLog

---

## Request ID Format

Subject format:

```text
[DR-TEST01] Monthly Production Report
```

The value inside square brackets is used as the Request ID.

---

## Database Objects

### ReportRequestMapping

Stores report configuration.

| Column          | Description                 |
| --------------- | --------------------------- |
| RequestID       | Unique Request Identifier   |
| StoredProcedure | Stored Procedure Name       |
| OutputFileName  | Output Excel Filename       |
| OneDriveFolder  | Destination OneDrive Folder |
| IsActive        | Enable / Disable Report     |

Example:

```sql
INSERT INTO dbo.ReportRequestMapping
(
    RequestID,
    StoredProcedure,
    OutputFileName,
    OneDriveFolder,
    IsActive
)
VALUES
(
    'AR-TEST03',
    'dbo.SP_TEST03',
    'TEST>1MILROW',
    'ReportAutomation/Test',
    1
);
```

---

### EmailAutomationLog

Stores processing history.

| Column       | Description              |
| ------------ | ------------------------ |
| MessageID    | Email Message Identifier |
| RequestID    | Request Identifier       |
| ProcessDate  | Processing Timestamp     |
| Status       | SUCCESS / FAILED         |
| OneDriveLink | Generated Share Link     |
| ErrorMessage | Failure Reason           |

---

## Security

### ZIP Encryption

Generated reports are protected using AES ZIP encryption.

Password format:

```text
{PASSWORD_PREFIX}{CURRENT_YEAR}
```

Example:

```text
BRINS2026
```

Password prefix is configurable through:

```ini
[zip]
password-prefix=BRINS
```

---

## Technologies Used

* Python
* Microsoft Graph API
* Microsoft OneDrive
* SQL Server
* PyODBC
* Pandas
* OpenPyXL
* PyZipper
* Windows Task Scheduler

---

## Scheduling

The automation is configured to run:

```text
Start Time : 09:00
Frequency  : Every 1 Hour
End Time   : 23:00
```

Using Windows Task Scheduler.

---

## Benefits

### Operational Efficiency

* Eliminates repetitive manual report generation.
* Reduces report delivery time.

### Standardization

* Consistent report delivery process.
* Consistent file naming convention.
* Consistent distribution method.

### Auditability

* Full processing history.
* Error tracking.
* Duplicate prevention.

### Scalability

New reports can be added without modifying Python code.

Only a new record is required in:

```sql
dbo.ReportRequestMapping
```

---

## Future Enhancements

### Phase 2

* Service Principal Authentication
* Fully unattended execution
* Multi-mailbox support
* Report usage analytics
* Dashboard monitoring

### Phase 3

* Conversational Analytics Integration
* Natural Language Report Requests
* AI-based Request Classification
* Automated Data Quality Validation

---

## Author

Initiator:
Erlangga Riyyan Nugraha

Department:
Data Management Department

Organization:
BRI Insurance

Year:
2026

## Architecture
report-automation/
│
├── report_bot.py              # Main program
├── config.ini
├── requirements.txt
│
├── modules/
│   ├── auth.py                # Microsoft Graph login
│   ├── mail.py                # Read mail / reply all
│   ├── database.py            # SQL functions
│   ├── exporter.py            # Excel export
│   ├── zipper.py              # Password ZIP
│   └── onedrive.py            # Upload + Share Link
│
└── logs/
    └── report_bot.log