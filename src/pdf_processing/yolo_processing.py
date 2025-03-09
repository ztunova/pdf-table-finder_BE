import os
import pymupdf
from src.constants import PATH_TO_IMGS, PATH_TO_PDFS
from src.custom_types.interfaces import (TableDataExtractionInterface, TableFindingInterface)
from src.file_handler import FileHandler



class YoloProcessing(TableFindingInterface, TableDataExtractionInterface):

    def __init__(self):
        super().__init__()
        self.fileHandler = FileHandler()

    def get_location_of_tables(self):
        pass

    def extract_tabular_data(self):
        pass

    def __pdf_to_img__(self):
        if not os.path.exists(PATH_TO_IMGS):
            os.makedirs(PATH_TO_IMGS)

        file_name_with_dir = self.fileHandler.get_pdf_name_with_directory()
        doc = pymupdf.open(file_name_with_dir)
        for page in doc:
            save_img_path = PATH_TO_IMGS + "/page-%i.png" % page.number
            pix = page.get_pixmap(dpi=900)
            pix.save(save_img_path)
