# database.py
import pyodbc
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read("config.ini")

def get_connection(config):

    return pyodbc.connect(
        f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={config['sql']['server']};
        DATABASE={config['sql']['database']};
        UID={config['sql']['username']};
        PWD={config['sql']['password']};
        """
    )

def get_mapping(conn, request_id):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            RequestID,
            StoredProcedure,
            OutputFileName,
            OneDriveFolder
        FROM dbo.ReportRequestMapping
        WHERE RequestID = ?
        AND IsActive = 1
    """, request_id)

    row = cursor.fetchone()

    if not row:
        return None

    return {
        "request_id": row.RequestID,
        "stored_procedure": row.StoredProcedure,
        "output_file": row.OutputFileName,
        "folder": row.OneDriveFolder
    }

def is_conversation_processed(
    conn,
    conversation_id
):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1
        FROM dbo.EmailAutomationLog
        WHERE ConversationID = ? AND Status = 'SUCCESS'
    """, conversation_id)

    return cursor.fetchone() is not None

# def is_processed(conn, message_id):

#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT 1
#         FROM dbo.EmailAutomationLog
#         WHERE MessageID = ?
#     """, message_id)

#     return cursor.fetchone() is not None

def log_success(
    conn,
    message_id,
    conversation_id,
    request_id,
    subject,
    sender_email,
    share_link
):

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO dbo.EmailAutomationLog
        (
            MessageID,
            ConversationID,
            RequestID,
            Subject,
            SenderEmail,
            ProcessDate,
            Status,
            OneDriveLink,
            ErrorMessage
        )
        VALUES
        (
            ?, ?, ?, ?, ?,
            GETDATE(),
            'SUCCESS',
            ?,
            NULL
        )
    """,
    message_id,
    conversation_id,
    request_id,
    subject,
    sender_email,
    share_link
    )

    conn.commit()

def log_failure(
    conn,
    message_id,
    conversation_id,
    request_id,
    subject,
    sender_email,
    error_message
):

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO dbo.EmailAutomationLog
        (
            MessageID,
            ConversationID,
            RequestID,
            Subject,
            SenderEmail,
            ProcessDate,
            Status,
            OneDriveLink,
            ErrorMessage
        )
        VALUES
        (
            ?, ?, ?, ?, ?,
            GETDATE(),
            'FAILED',
            NULL,
            ?
        )
    """,
    message_id,
    conversation_id,
    request_id,
    subject,
    sender_email,
    str(error_message)
    )

    conn.commit()


def execute_sp(
        conn,
        stored_procedure):

    query = f"EXEC {stored_procedure}"

    return pd.read_sql(
        query,
        conn
    )