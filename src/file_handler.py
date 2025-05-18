import os
import shutil

import pymupdf

from src.constants import PATH_TO_IMGS, PATH_TO_PDFS, PATH_TO_RESULTS
from src.exceptions.custom_exceptions import NotAPdfFileException


class FileHandler:
    def __init__(self):
        if not os.path.exists(PATH_TO_PDFS):
            os.makedirs(PATH_TO_PDFS)

        if not os.path.exists(PATH_TO_IMGS):
            os.makedirs(PATH_TO_IMGS)

        if not os.path.exists(PATH_TO_RESULTS):
            os.makedirs(PATH_TO_RESULTS)

    def get_directory_content(self, directory_path: str) -> list[str]:
        directory_content: list[str] = os.listdir(directory_path)
        return directory_content

    # strany cislovane od 0
    def __pdf_to_images(self, file_name: str) -> None:
        # get location where pdf converted to imgs will be stored
        file_name_without_extension = file_name.removesuffix(".pdf")
        pdf_as_imgs_location = os.path.join(PATH_TO_IMGS, file_name_without_extension)
        if not os.path.exists(pdf_as_imgs_location):
            os.makedirs(pdf_as_imgs_location)

        # convert pdf to imgs and save to corresponding location
        pdf_name_with_dir = os.path.join(PATH_TO_PDFS, file_name)
        doc = pymupdf.open(pdf_name_with_dir)
        for page in doc:
            save_img_path = pdf_as_imgs_location + "/page-%i.png" % page.number
            pix = page.get_pixmap(dpi=900)
            pix.save(save_img_path)

    def upload_pdf_file(self, file, pdf_id: str):
        if not file.filename.endswith(".pdf"):
            raise NotAPdfFileException()

        # append id to the file
        filename_without_extension = file.filename.removesuffix(".pdf")
        filename_with_id = f"{filename_without_extension}__{pdf_id}.pdf"

        all_pdfs = self.get_directory_content(PATH_TO_PDFS)
        if filename_with_id in all_pdfs:
            self.clean_up_pdf(filename_with_id)

        file_with_path = os.path.join(PATH_TO_PDFS, filename_with_id)

        # Save the uploaded file
        with open(file_with_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        self.__pdf_to_images(file_name=filename_with_id)

    def clean_up_pdf(self, pdf_name):
        # delete pdf
        # delete pdf images
        pdf_path = os.path.join(PATH_TO_PDFS, pdf_name)
        pdf_imgs_path = os.path.join(PATH_TO_IMGS, pdf_name.removesuffix(".pdf"))
        try:
            os.remove(pdf_path)
            shutil.rmtree(pdf_imgs_path)
        except FileNotFoundError:
            print(f"File already deleted: {pdf_path}")
