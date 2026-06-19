from modules.database import *

conn = get_connection(config)

mapping = get_mapping(
    conn,
    "AR-TEST02"
)

print(mapping)