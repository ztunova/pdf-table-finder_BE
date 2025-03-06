import pymupdf
from src.custom_types.interfaces import (
    TableDataExtractionInterface,
    TableFindingInterface,
)
import os


class YoloProcessing(
    TableFindingInterface,
    TableDataExtractionInterface,
):
    def get_location_of_tables(
        self,
        pdf_document,
    ):
        pass

    def extract_tabular_data(
        self,
    ):
        pass

    def __pdf_to_img__(
        file_dir: str,
        file_name: str,
    ):
        file_name = "/" + file_name
        file_name_with_dir = file_dir + file_name
        save_img_directory = (
            r"/mnt/c/Users/zofka/OneDrive/Dokumenty/Brno/FI_MUNI/SDIPR_Diplomovka/testing_16-12-24_pdf_to_img"
            + file_name.removesuffix(".pdf")
            + pages_dir_suffix
        )
        if not os.path.exists(save_img_directory):
            os.makedirs(save_img_directory)

        doc = pymupdf.open(file_name_with_dir)
        for page in doc:
            save_img_path = save_img_directory + "/page-%i.png" % page.number
            pix = page.get_pixmap(dpi=900)
            pix.save(save_img_path)
