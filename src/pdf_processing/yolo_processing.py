import os
import pymupdf
from src.constants import PATH_TO_IMGS, PATH_TO_PDFS
from src.custom_types.interfaces import (TableDataExtractionInterface, TableFindingInterface)



class YoloProcessing(TableFindingInterface, TableDataExtractionInterface):
    def get_location_of_tables(self):
        pass

    def extract_tabular_data(self):
        pass

    def __pdf_to_img__():
        if not os.path.exists(PATH_TO_IMGS):
            os.makedirs(PATH_TO_IMGS)

        pdf_file_name = os.listdir(PATH_TO_PDFS)[0]
        file_name_with_dir = PATH_TO_PDFS + '/' + pdf_file_name
        doc = pymupdf.open(file_name_with_dir)
        for page in doc:
            save_img_path = PATH_TO_IMGS + "/page-%i.png" % page.number
            pix = page.get_pixmap(dpi=900)
            pix.save(save_img_path)
