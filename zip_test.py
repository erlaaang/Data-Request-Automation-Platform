from modules.zipper import create_zip

zip_path = create_zip(
    source_file="temp/test.xlsx",
    zip_file="temp/test.zip",
    password="BRINS2026"
)

print(zip_path)