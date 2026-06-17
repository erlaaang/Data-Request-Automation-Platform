"""Quick export test script."""

from modules.database import config, execute_sp, get_connection
from modules.exporter import export_to_excel

conn = get_connection(config)

df = execute_sp(
    conn,
    "dbo.sp_test02"
)

file_path = export_to_excel(
    df,
    "temp",
    "test.xlsx"
)

print(file_path)