# exporter.py
import os
import pandas as pd


def export_to_excel(
        df,
        output_folder,
        output_filename):

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    excel_path = os.path.join(
        output_folder,
        output_filename
    )

    df.to_excel(
        excel_path,
        index=False
    )

    return excel_path