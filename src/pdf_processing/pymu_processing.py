import os
import pymupdf
from src.constants import PATH_TO_PDFS
from src.custom_types.api_types import Point, SingleTableRequest
from src.custom_types.interfaces import TableExtractionInterface, TableDetectionInterface
from src.file_handler import FileHandler
from src.service.service_helper import ServiceHelper


class PymuProcessing(TableDetectionInterface, TableExtractionInterface):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.helper = ServiceHelper()

    # returns coordinates of top lef and bottom right corner
    def detect_tables(self, pdf_name: str):
        pdf_with_dir = os.path.join(PATH_TO_PDFS, pdf_name)
        doc = pymupdf.open(pdf_with_dir)
        all_tables_in_doc = {}
        for page in doc:
            page_width = page.rect.width
            page_height = page.rect.height

            tables_on_page = page.find_tables()
            tables_on_page_bboxes = []
            for table in tables_on_page.tables:
                page.draw_rect(table.bbox, color=(0, 1, 0), width=2)
                page.draw_line((table.bbox[0], table.bbox[1]), (table.bbox[2], table.bbox[3]), color=(0, 1, 0), width=2)
                table_coords = Point(
                    upperLeftX=table.bbox[0],
                    upperLeftY=table.bbox[1],
                    lowerRightX=table.bbox[2],
                    lowerRightY=table.bbox[3],
                )

                percentage_coords = self.helper.absolute_coords_to_percentage(table_coords, page_width, page_height)
                tables_on_page_bboxes.append(percentage_coords)
            all_tables_in_doc[page.number] = tables_on_page_bboxes

        return all_tables_in_doc

    def extract_tabular_data(self, pdf_name: str, rectangle_data: SingleTableRequest):
        pdf_with_dir = os.path.join(PATH_TO_PDFS, pdf_name)
        doc = pymupdf.open(pdf_with_dir)
        page = doc[rectangle_data.pdf_page_number]
        page_width = page.rect.width
        page_height = page.rect.height

        absolute_coords = self.helper.percentage_coords_to_absolute(rectangle_data, page_width, page_height)
        table_box = (
            absolute_coords.upper_left_x,
            absolute_coords.upper_left_y,
            absolute_coords.lower_right_x,
            absolute_coords.lower_right_y,
        )
        page.draw_rect(table_box, color=(1, 0, 0), width=2)

        found_tables = page.find_tables(
            clip=table_box, horizontal_strategy="text", vertical_strategy="text", min_words_horizontal=3
        ).tables

        if not found_tables or len(found_tables) == 0:
            # No tables found
            return []

        rows = []
        for table in found_tables:
            rows.extend(table.extract())

        return rows
