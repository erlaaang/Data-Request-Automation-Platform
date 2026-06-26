from modules.database import get_connection, config

conn = get_connection(config)
cur = conn.cursor()
pattern = '%WP_ROEAST%'
print('Searching for object names matching', pattern)
cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE ?", pattern)
rows = cur.fetchall()
for schema, name in rows:
    print('TABLE:', schema, name)
cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME LIKE ?", pattern)
rows = cur.fetchall()
for schema, name in rows:
    print('VIEW :', schema, name)

cur.execute("SELECT TOP 20 s.name, o.name, o.type_desc FROM sys.objects o JOIN sys.schemas s ON o.schema_id = s.schema_id WHERE o.name LIKE ? ORDER BY o.name", '%WP_ROEAST%')
rows = cur.fetchall()
for schema, name, typ in rows:
    print('SYS  :', schema, name, typ)
