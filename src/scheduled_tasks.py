import datetime
import os
import shutil
from src.constants import PATH_TO_IMGS, PATH_TO_PDFS


def clean_unused_files():
    print("Starting scheduled cleaning...")
    all_pdfs = os.listdir(PATH_TO_PDFS)
    current_datetime = datetime.datetime.now()
    for pdf_file in all_pdfs:
        pdf_with_path = os.path.join(PATH_TO_PDFS, pdf_file)
        last_access_timestamp = os.path.getatime(pdf_with_path)
        last_access_datetime = datetime.datetime.fromtimestamp(last_access_timestamp)
        
        time_difference = current_datetime - last_access_datetime
        print(f"File {pdf_file} last assessed {last_access_datetime}, age {time_difference}")
        if time_difference > datetime.timedelta(days=2):
            pdf_imgs_path = os.path.join(PATH_TO_IMGS, pdf_file.removesuffix(".pdf"))
            try:
                print(f"Deleting {pdf_file} with images location {pdf_imgs_path}")
                os.remove(pdf_with_path)
                shutil.rmtree(pdf_imgs_path)
                print(f'{pdf_file} cleaned successfully')
            except FileNotFoundError:
                print(f"Error cleaning file {pdf_file}")
    print("Scheduled cleaning finished")
