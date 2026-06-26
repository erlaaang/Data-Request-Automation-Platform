import os
import math
import pandas as pd

ROWS_PER_FILE = 1_000_000

def get_total_rows(
        conn,
        table_name):

    cursor = conn.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM Tampungan.dbo.{table_name}"
    )

    return cursor.fetchone()[0]


def export_to_excel(
        conn,
        table_name,
        output_folder,
        output_filename,
        order_by_column=None):

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    total_rows = get_total_rows(
        conn,
        table_name
    )

    print(
        f"[EXPORT] Total rows: {total_rows:,}"
    )

    if total_rows == 0:
        raise Exception(
            f"No data found in {table_name}"
        )

    total_parts = math.ceil(
        total_rows / ROWS_PER_FILE
    )

    print(
        f"[EXPORT] Total files: {total_parts}"
    )

    file_paths = []

    for part in range(total_parts):

        offset = part * ROWS_PER_FILE

        print(
            f"[EXPORT] Processing part {part + 1}/{total_parts}"
        )

        if order_by_column:

            query = f"""
                SELECT *
                FROM Tampungan.dbo.{table_name}
                ORDER BY {order_by_column}
                OFFSET {offset} ROWS
                FETCH NEXT {ROWS_PER_FILE} ROWS ONLY
            """

        else:

            query = f"""
                SELECT *
                FROM Tampungan.dbo.{table_name}
                ORDER BY (SELECT NULL)
                OFFSET {offset} ROWS
                FETCH NEXT {ROWS_PER_FILE} ROWS ONLY
            """

        print(
            f"[EXPORT] Loading rows {offset:,} - "
            f"{min(offset + ROWS_PER_FILE, total_rows):,}"
        )

        df = pd.read_sql(
            query,
            conn
        )

        if total_parts == 1:

            file_name = (
                f"{output_filename}.xlsx"
            )

        else:

            file_name = (
                f"{output_filename}_Part{part + 1}.xlsx"
            )

        file_path = os.path.join(
            output_folder,
            file_name
        )

        print(
            f"[EXPORT] Writing {file_name}"
        )

        with pd.ExcelWriter(
                file_path,
                engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Data"
            )

        file_paths.append(
            file_path
        )

        print(
            f"[EXPORT] Completed {file_name}"
        )

    print(
        f"[EXPORT] Export Finished "
        f"({len(file_paths)} files)"
    )

    return file_paths