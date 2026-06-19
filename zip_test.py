from modules.zipper import create_zip

zip_path = create_zip(
    source_files="temp/test1.xlsx&&temp/test2",
    zip_file="temp/test.zip",
    password="BRINS2026"
)

print(zip_path)