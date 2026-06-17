from modules.database import *

conn = get_connection(config)

mapping = get_mapping(
    conn,
    "DR-TEST01"
)

print(mapping)