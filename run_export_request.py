from modules.database import get_connection, get_mapping, config
from modules.exporter import export_to_excel

req = 'AR-WPROESB'

try:
    conn = get_connection(config)
    mapping = get_mapping(conn, req)
    print('Mapping:', mapping)

    if not mapping:
        raise SystemExit('Mapping not found')

    files = export_to_excel(
        conn,
        mapping['final_table'],
        'temp',
        mapping['output_file'],
        mapping.get('order_by_column'),
        mapping.get('split_column')
    )

    print('Exported files:\n', '\n'.join(files))

except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()
