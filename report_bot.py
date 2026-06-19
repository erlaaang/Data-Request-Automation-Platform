import os
import traceback
import configparser

from modules.auth import get_token
from modules.database import (
    get_connection,
    get_mapping,
    execute_sp,
    is_conversation_processed,
    log_success,
    log_failure
)

from modules.mail import (
    get_unread_requests,
    extract_request_id,
    reply_all,
    mark_as_read
)

from modules.exporter import export_to_excel, get_total_rows

from modules.zipper import create_zip

from modules.onedrive import (
    upload_file,
    create_share_link
)

from modules.logger import setup_logger

from modules.utils import (
    build_zip_password,
    safe_delete
)


def main():

    logger = setup_logger()

    logger.info("===================================")
    logger.info("REPORT BOT STARTED")
    logger.info("===================================")

    config = configparser.ConfigParser()
    config.read("config.ini")

    try:

        logger.info("Authenticating Graph")

        token = get_token(config)

        mailbox = config["graph"]["mailbox"]
        drivebox = config["graph"]["drivebox"]

        logger.info("Graph Authentication Success")

        logger.info("Connecting SQL Server")

        conn = get_connection(config)

        logger.info("SQL Connection Success")

        emails = get_unread_requests(
            token,
            mailbox
        )

        logger.info(
            f"Found {len(emails)} request(s)"
        )

        for email in emails:

            message_id = email["id"]
            subject = email["subject"]
            conversation_id = email.get(
                "conversationId"
            )

            sender_email = (
                email.get("from", {})
                    .get("emailAddress", {})
                    .get("address", "")
            )

            logger.info(
                f"Processing: {subject}"
            )

            request_id = extract_request_id(
                subject
            )

            if not request_id:

                logger.warning(
                    "Request ID not found"
                )

                continue

            if is_conversation_processed(
                conn,
                conversation_id
            ):

                logger.info(
                    "Already Processed"
                )

                continue

            try:

                mapping = get_mapping(
                    conn,
                    request_id
                )

                if not mapping:

                    raise Exception(
                        f"Mapping not found: {request_id}"
                    )

                logger.info(
                    f"Executing SP: {mapping['stored_procedure']}"
                )

                execute_sp(
                    conn,
                    mapping["stored_procedure"]
                )

                totalrow = get_total_rows(
                    conn,
                    mapping["final_table"]
                )

                logger.info(
                    f"Rows Returned: {totalrow}"
                )

                excel_name = (
                    mapping["output_file"]
                )

                excel_path = (
                    f"temp/{excel_name}.xlsx"
                )

                logger.info(
                    "Exporting Excel"
                )

                excel_files = export_to_excel(
                    conn,
                    mapping["Final_Table"],
                    "temp",
                    mapping["OutputFileName"],
                    mapping["OrderByColumn"]
                )

                password = (
                    build_zip_password(config)
                )

                zip_path = (
                    f"temp/{excel_name}.zip"
                )

                logger.info(
                    "Creating ZIP"
                )

                create_zip(
                    excel_files,
                    zip_path,
                    password
                )

                logger.info(
                    "Uploading OneDrive"
                )

                item_id = upload_file(
                    token,
                    drivebox,
                    zip_path,
                    mapping["folder"],
                    os.path.basename(zip_path)
                )

                logger.info(
                    f"Item ID: {item_id}"
                )

                share_link = create_share_link(
                    token,
                    drivebox,
                    item_id
                )

                logger.info(
                    "Replying Email"
                )

                reply_all(
                    token,
                    mailbox,
                    message_id,
                    share_link,
                    request_id
                )

                logger.info(
                    "Marking Email Read"
                )

                mark_as_read(
                    token,
                    mailbox,
                    message_id
                )

                log_success(
                    conn,
                    message_id,
                    conversation_id,
                    request_id,
                    subject,
                    sender_email,
                    share_link
                )

                logger.info(
                    f"SUCCESS: {request_id}"
                )

                safe_delete(
                    excel_path
                )

                safe_delete(
                    zip_path
                )

            except Exception as e:

                logger.error(str(e))

                log_failure(
                    conn,
                    message_id,
                    conversation_id,
                    request_id,
                    subject,
                    sender_email,
                    str(e)
                )

                logger.error(
                    traceback.format_exc()
                )

        logger.info(
            "BOT FINISHED"
        )

    except Exception as e:

        logger.error(
            f"FATAL ERROR: {e}"
        )

        logger.error(
            traceback.format_exc()
        )


if __name__ == "__main__":
    main()