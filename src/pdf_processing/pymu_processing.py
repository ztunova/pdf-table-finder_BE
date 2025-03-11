import pymupdf
from src.custom_types.api_types import SingleTableRequest
from src.custom_types.interfaces import TableDataExtractionInterface, TableDetectionInterface
from src.file_handler import FileHandler


class PymuProcessing(TableDetectionInterface, TableDataExtractionInterface):
    def __init__(self):
        super().__init__()
        self.fileHandler = FileHandler()

    def detect_tables(self):
        pdf_with_dir = self.fileHandler.get_pdf_name_with_directory()
        doc = pymupdf.open(pdf_with_dir)
        all_tables_in_doc = {}
        for page in doc:
            tables_on_page = page.find_tables()
            tables_on_page_bboxes = []
            for table in tables_on_page.tables:
                tables_on_page_bboxes.append(table.bbox)
            all_tables_in_doc[page.number] = tables_on_page_bboxes

        return all_tables_in_doc

    def extract_tabular_data(self, rectangle_data: SingleTableRequest):
        pdf_with_dir = self.fileHandler.get_pdf_name_with_directory()
        doc = pymupdf.open(pdf_with_dir)
        page = doc[rectangle_data.pdf_page_number]
        table_box = (
            rectangle_data.upper_left_x,
            rectangle_data.upper_left_y,
            rectangle_data.rect_width,
            rectangle_data.rect_height,
        )
        tables = page.find_tables(
            clip=table_box, horizontal_strategy="text", vertical_strategy="text", min_words_horizontal=3
        )
        for table in tables:
            print(table.to_markdown())
