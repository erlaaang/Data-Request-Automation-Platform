from modules.database import get_connection, config
import pandas as pd

conn = get_connection(config)
query = "SELECT TOP 5 * FROM Tampungan.dbo.WP_ROEAST"
df = pd.read_sql(query, conn)
print('Columns:', df.columns.tolist())
print('Rows:', len(df))
print(df.head().to_dict(orient='records'))
