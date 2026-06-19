# zipper.py
import os
import pyzipper


def create_zip(
    source_files,
    zip_file,
    password
    ):

    os.makedirs(
        os.path.dirname(zip_file),
        exist_ok=True
    )

    with pyzipper.AESZipFile(
            zip_file,
            "w",
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES
    ) as zf:

        zf.setpassword(
            password.encode()
        )

        for file in source_files:

            zf.write(
                file,
                arcname=os.path.basename(file)
            )

    return zip_file