import math
import os
import zipfile
from pathlib import Path

import pandas as pd

try:
    import pyzipper
except ImportError:  # pragma: no cover - optional dependency fallback
    pyzipper = None

EXCEL_LIMIT = 1_000_000
ROWS_PER_FILE = 1_000_000


def get_total_rows(conn, table_name):
    """Return the row count for a table in the configured SQL server database."""
    cursor = conn.cursor()
    table_ref = table_name if "." in table_name else f"Tampungan.dbo.{table_name}"
    cursor.execute(f"SELECT COUNT(*) FROM {table_ref}")
    row = cursor.fetchone()
    return int(row[0]) if row else 0


def sanitize_filename(name):
    """Clean a file name so it is safe for Excel and ZIP exports."""
    if name is None:
        return "export"

    cleaned = str(name).strip()
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        cleaned = cleaned.replace(char, "")

    cleaned = cleaned.replace("\x00", "")
    cleaned = cleaned.replace(" ", "_")
    return cleaned or "export"


def _ensure_excel_extension(filename):
    name = sanitize_filename(filename)
    base, ext = os.path.splitext(name)
    if ext.lower() != ".xlsx":
        return f"{base}.xlsx"
    return name


def save_excel(df, file_path, sheet_name="Data"):
    """Write a pandas DataFrame to an Excel file."""
    if df is None:
        raise ValueError("DataFrame cannot be None")

    resolved_path = str(file_path)
    if not resolved_path.lower().endswith(".xlsx"):
        resolved_path = f"{resolved_path}.xlsx"

    output_path = Path(resolved_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    return str(output_path)


def export_single(df, output_folder, output_filename, sheet_name="Data"):
    """Write a single DataFrame to a single Excel file."""
    output_folder = str(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    file_name = _ensure_excel_extension(output_filename)
    file_path = os.path.join(output_folder, file_name)
    return save_excel(df, file_path, sheet_name=sheet_name)


def export_by_rows(df, output_folder, output_filename, sheet_name="Data", rows_per_file=EXCEL_LIMIT):
    """Split a DataFrame into multiple Excel files by row count."""
    if df is None or df.empty:
        raise ValueError("DataFrame is empty")

    output_folder = str(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    if len(df) <= rows_per_file:
        return [export_single(df, output_folder, output_filename, sheet_name=sheet_name)]

    file_paths = []
    for part, start in enumerate(range(0, len(df), rows_per_file), start=1):
        chunk = df.iloc[start:start + rows_per_file]
        part_name = f"{output_filename}_Part{part}"
        file_path = export_single(chunk, output_folder, part_name, sheet_name=sheet_name)
        file_paths.append(file_path)

    return file_paths


def split_into_parts(df, output_folder, output_filename, sheet_name="Data", rows_per_file=EXCEL_LIMIT):
    """Backward-compatible alias for export_by_rows."""
    return export_by_rows(df, output_folder, output_filename, sheet_name=sheet_name, rows_per_file=rows_per_file)


def export_by_group(df, split_column, output_folder, output_filename, sheet_name="Data", rows_per_file=EXCEL_LIMIT):
    """Split a DataFrame into Excel files based on a column value."""
    if df is None or df.empty:
        raise ValueError("DataFrame is empty")

    # Case-insensitive column lookup
    actual_column = None
    for col in df.columns:
        if col.lower() == split_column.lower():
            actual_column = col
            break

    if actual_column is None:
        raise KeyError(f"Column '{split_column}' was not found. Available columns: {df.columns.tolist()}")

    output_folder = str(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    file_paths = []
    for value in df[actual_column].dropna().unique():
        group_df = df[df[split_column] == value]
        safe_value = sanitize_filename(value)
        if len(group_df) <= rows_per_file:
            file_path = export_single(group_df, output_folder, f"{output_filename}_{safe_value}", sheet_name=sheet_name)
        else:
            file_path = split_into_parts(group_df, output_folder, f"{output_filename}_{safe_value}", sheet_name=sheet_name, rows_per_file=rows_per_file)
            file_paths.extend(file_path)
            continue

        file_paths.append(file_path)

    return file_paths


def export_report():
    """Placeholder for future reporting workflows."""
    return None


def load_data():
    """Placeholder for future data-loading workflows."""
    return None


def export_to_excel(conn, table_name, output_folder, output_filename, order_by_column=None, split_column=None):
    """Export a SQL table to one or more Excel files and return their paths."""
    os.makedirs(output_folder, exist_ok=True)

    total_rows = get_total_rows(conn, table_name)
    if total_rows == 0:
        raise Exception(f"No data found in {table_name}")

    table_ref = table_name if "." in table_name else f"Tampungan.dbo.{table_name}"

    if split_column:
        if order_by_column:
            query = f"SELECT * FROM {table_ref} ORDER BY {order_by_column}"
        else:
            query = f"SELECT * FROM {table_ref}"

        df = pd.read_sql(query, conn)
        if df.empty:
            return []

        return export_by_group(df, split_column, output_folder, output_filename)

    total_parts = math.ceil(total_rows / ROWS_PER_FILE)
    file_paths = []

    for part in range(total_parts):
        offset = part * ROWS_PER_FILE

        if order_by_column:
            query = f"SELECT * FROM {table_ref} ORDER BY {order_by_column} OFFSET {offset} ROWS FETCH NEXT {ROWS_PER_FILE} ROWS ONLY"
        else:
            query = f"SELECT * FROM {table_ref} ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {ROWS_PER_FILE} ROWS ONLY"

        df = pd.read_sql(query, conn)
        if df.empty:
            continue

        if total_parts == 1:
            file_name = _ensure_excel_extension(output_filename)
        else:
            file_name = f"{_ensure_excel_extension(output_filename).replace('.xlsx', '')}_Part{part + 1}.xlsx"

        file_path = os.path.join(output_folder, file_name)
        save_excel(df, file_path)
        file_paths.append(file_path)

    return file_paths


def zip_reports(file_paths, output_zip_path, password=None):
    """Create a ZIP archive from one or more files."""
    output_zip_path = str(output_zip_path)
    if not output_zip_path.lower().endswith(".zip"):
        output_zip_path = f"{output_zip_path}.zip"

    output_dir = os.path.dirname(output_zip_path) or "."
    os.makedirs(output_dir, exist_ok=True)

    if password:
        if pyzipper is None:
            raise ImportError("pyzipper is required for password-protected zip archives")

        with pyzipper.AESZipFile(output_zip_path, "w", compression=pyzipper.ZIP_DEFLATED) as zf:
            zf.setpassword(password.encode("utf-8"))
            for file_path in file_paths:
                zf.write(file_path, os.path.basename(file_path))
    else:
        with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in file_paths:
                zf.write(file_path, os.path.basename(file_path))

    return output_zip_path