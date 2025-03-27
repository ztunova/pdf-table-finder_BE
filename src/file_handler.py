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
        directory_content.remove("README.md")
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
    def __pdf_to_images(self) -> None:
        pdf_name_with_dir = self.get_pdf_name_with_directory()
        doc = pymupdf.open(pdf_name_with_dir)
        for page in doc:
            save_img_path = PATH_TO_IMGS + "/page-%i.png" % page.number
            pix = page.get_pixmap(dpi=900)
            pix.save(save_img_path)

    def upload_pdf_file(self, file):
        self.__clean_up_directory_content(PATH_TO_PDFS)
        self.__clean_up_directory_content(PATH_TO_IMGS)
        self.__clean_up_directory_content(PATH_TO_RESULTS)

        if not file.filename.endswith(".pdf"):
            raise NotAPdfFileException()

        file_with_path = os.path.join(PATH_TO_PDFS, file.filename)

        # Save the uploaded file
        with open(file_with_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        self.__pdf_to_images()
