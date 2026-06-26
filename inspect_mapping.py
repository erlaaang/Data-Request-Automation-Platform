from modules.database import get_connection, config

req = 'AR-WPROESB'
conn = get_connection(config)
cur = conn.cursor()
cur.execute("SELECT * FROM dbo.ReportRequestMapping WHERE RequestID = ?", req)
row = cur.fetchone()
if not row:
    print('No row')
else:
    cols = [d[0] for d in cur.description]
    print('Columns:', cols)
    print('Values:')
    for k, v in zip(cols, row):
        print(f'{k}: {v}')
    # print as dict
    print('\nAs dict:')
    print({k:v for k,v in zip(cols, row)})
