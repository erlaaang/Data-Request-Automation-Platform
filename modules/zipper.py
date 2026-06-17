# zipper.py
import os
import pyzipper


def create_zip(
        source_file,
        zip_file,
        password):

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

        zf.write(
            source_file,
            arcname=os.path.basename(source_file)
        )

    return zip_file