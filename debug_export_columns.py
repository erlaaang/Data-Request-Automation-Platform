from modules.database import get_connection, config
import pandas as pd

req = 'AR-WPROESB'
conn = get_connection(config)

# Load only a small sample of the target table for inspection
query = "SELECT TOP 5 * FROM WP_ROEAST"
df = pd.read_sql(query, conn)
print('Columns:', df.columns.tolist())
print('Rows:', len(df))
print(df.head().to_dict(orient='records'))
