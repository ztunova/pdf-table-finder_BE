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

    def get_pdf_name_with_directory(self) -> str:
        pdf_file_name: str = self.get_directory_content(PATH_TO_PDFS)[0]
        return os.path.join(PATH_TO_PDFS, pdf_file_name)

    def get_pdf_result_output(self) -> str:
        pdf_file_name: str = self.get_directory_content(PATH_TO_PDFS)[0]
        return os.path.join(PATH_TO_RESULTS, pdf_file_name)

    def __clean_up_directory_content(self, direcotry_path: str) -> None:
        dir_content: list[str] = self.get_directory_content(direcotry_path)
        for file_name in dir_content:
            path = os.path.join(direcotry_path, file_name)
            os.remove(path)

    # strany cislovane od 0
    def __pdf_to_images(self, file_name: str) -> None:
        # get location where pdf converted to imgs will be stored
        file_name_without_extension = file_name.removesuffix('.pdf')
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

    def upload_pdf_file(self, file):
        if not file.filename.endswith(".pdf"):
            raise NotAPdfFileException()
        
        all_pdfs = self.get_directory_content(PATH_TO_PDFS)
        if file.filename in all_pdfs:
            self.clean_up_pdf(file.filename)

        file_with_path = os.path.join(PATH_TO_PDFS, file.filename)

        # Save the uploaded file
        with open(file_with_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        self.__pdf_to_images(file_name=file.filename)

    def clean_up_pdf(self, pdf_name):
        # delete pdf
        # delete pdf images
        pdf_path = os.path.join(PATH_TO_PDFS, pdf_name)
        pdf_imgs_path = os.path.join(PATH_TO_IMGS, pdf_name.removesuffix('.pdf'))
        os.remove(pdf_path)
        shutil.rmtree(pdf_imgs_path)
