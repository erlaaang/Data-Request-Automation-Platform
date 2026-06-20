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
            FinalTable,
            OutputFileName,
            OrderByColumn,
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
        "final_table": row.FinalTable,
        "output_file": row.OutputFileName,
        "order_by_column": row.OrderByColumn,
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
                   
        IF EXISTS
        (
            SELECT 1
            FROM dbo.EmailAutomationLog
            WHERE MessageID = ?
        )
        BEGIN
            DELETE FROM dbo.EmailAutomationLog WHERE MessageID = ?
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
        END
        ELSE
                                                          
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
    message_id,
    message_id,
    conversation_id,
    request_id,
    subject,
    sender_email,
    share_link,
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
    IF EXISTS
    (
        SELECT 1
        FROM dbo.EmailAutomationLog
        WHERE MessageID = ?
    )
    BEGIN

        UPDATE dbo.EmailAutomationLog
        SET
            Status = 'FAILED',
            ErrorMessage = ?
        WHERE MessageID = ?

    END
    ELSE
    BEGIN

        INSERT INTO dbo.EmailAutomationLog
        (
            MessageID,
            ConversationID,
            RequestID,
            Subject,
            SenderEmail,
            ProcessDate,
            Status,
            ErrorMessage
        )
        VALUES
        (
            ?, ?, ?, ?, ?,
            GETDATE(),
            'FAILED',
            ?
        )

    END
    """,
    message_id,
    str(error_message),
    message_id,
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
    stored_procedure
):
    """Execute a stored procedure and commit the transaction."""
    print(f"Executing {stored_procedure}... This may take a while.")

    cursor = conn.cursor()

    cursor.execute(f"EXEC {stored_procedure}")
    conn.commit()

    print("SP Completed")

def get_total_rows(
    conn,
    table_name
):

    cursor = conn.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM Tampungan.dbo.{table_name}"
    )

    return cursor.fetchone()[0]