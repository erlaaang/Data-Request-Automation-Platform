# BRINS Report Automation Platform

## Overview

BRINS Report Automation Platform is an automated email-driven reporting system developed to reduce manual effort in fulfilling recurring data requests.

The platform monitors incoming Outlook emails, identifies report requests based on predefined request IDs, executes SQL Server stored procedures, generates Excel reports, uploads them to OneDrive, and automatically replies to the requester with a download link.

---

## Features

### Email Automation

* Monitor incoming Outlook emails using Microsoft Graph API
* Detect report requests based on Request ID
* Prevent duplicate processing
* Automatically reply to requesters using Reply All
* Mark processed emails as read

### Report Generation

* Execute SQL Server stored procedures
* Export large datasets to Excel
* Automatically split files exceeding Excel row limits (1,000,000 rows per file)
* Generate ZIP archives when multiple Excel files are produced

### OneDrive Integration

* Upload generated reports to OneDrive
* Generate shareable download links
* Include download links in automated email responses

### Logging & Monitoring

* Track successful report deliveries
* Track failed executions
* Store processing history in SQL Server
* Prevent duplicate processing using Message ID validation

---

## Architecture

```text
Outlook Mailbox
       │
       ▼
Microsoft Graph API
       │
       ▼
Python Automation Service
       │
       ├── Request Validation
       │
       ├── SQL Server Stored Procedure
       │
       ├── Excel Export
       │
       ├── ZIP Packaging
       │
       ├── OneDrive Upload
       │
       └── Automated Reply
       │
       ▼
SQL Server Logging
```

---

## Technology Stack

### Backend

* Python 3.x
* Requests
* Pandas
* OpenPyXL
* PyODBC

### Database

* Microsoft SQL Server

### Email Service

* Microsoft Graph API
* Outlook Online

### File Storage

* Microsoft OneDrive
* SharePoint Online

---

## Project Structure

```text
Data-Request-Automation-Platform/
│
├── report_bot.py
│
├── config.ini
│
├── modules/
│   ├── auth.py
│   ├── database.py
│   ├── exporter.py
│   ├── mail.py
│   ├── onedrive.py
│   └── logger.py
│
├── logs/
│
└── output/
```

---

## Processing Flow

### 1. Receive Request

Example email subject:

```text
[AR-WPAKUA119] Permohonan Data Detail Produksi AKUA
```

### 2. Validate Request

The system extracts:

```text
AR-WPAKUA119
```

and checks whether a report mapping exists.

### 3. Execute Stored Procedure

Configured stored procedure:

```sql
EXEC dbo.SPAR_WPAKUA119
```

### 4. Export Result

The generated dataset is exported to Excel.

If the result exceeds 1 million rows:

```text
Report_Part_1.xlsx
Report_Part_2.xlsx
Report_Part_3.xlsx
...
```

### 5. Upload to OneDrive

Generated files are uploaded automatically to OneDrive.

### 6. Send Reply

The requester receives an automated reply containing a download link.

### 7. Log Result

Processing information is stored in:

```sql
dbo.EmailAutomationLog
```

---

## Logging Table

### EmailAutomationLog

| Column         | Description                 |
| -------------- | --------------------------- |
| MessageID      | Original Outlook Message ID |
| ConversationID | Email Conversation ID       |
| RequestID      | Report Request ID           |
| Subject        | Email Subject               |
| SenderEmail    | Request Sender              |
| ProcessDate    | Processing Timestamp        |
| Status         | SUCCESS / FAILED            |
| OneDriveLink   | Generated Report Link       |
| ErrorMessage   | Failure Details             |

---

## Duplicate Prevention

The platform prevents duplicate processing using:

* Message ID validation
* Logging table lookup
* Conversation tracking

This ensures the same request is never processed twice.

---

## Scheduler

The application is designed to run through:

### Windows Task Scheduler

Example:

```text
Every 15 minutes
```

or

### SQL Server Agent

for enterprise deployment.

---

## Future Enhancements

* Web dashboard for request monitoring
* Grafana integration
* Microsoft Teams notifications
* Dynamic request configuration
* Self-service report portal
* AI-assisted report categorization

---

## Author

Erlangga Riyyan Nugraha

Data Architect | BRI Insurance

Specialized in:

* Data Architecture
* SQL Server
* ETL & Automation
* Reporting Solutions
* Data Governance
