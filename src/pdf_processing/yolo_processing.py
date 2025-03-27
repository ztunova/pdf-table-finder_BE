import os
import cv2
import easyocr
import numpy as np
from PIL import Image
import pandas
from ultralyticsplus import YOLO, render_result
from src.constants import PATH_TO_IMGS
from src.custom_types.api_types import Point, SingleTableRequest
from src.custom_types.interfaces import TableExtractionInterface, TableDetectionInterface
from src.custom_types.table_types import TableRow, TableWord
from src.exceptions.custom_exceptions import NoTableException
from src.file_handler import FileHandler
from src.service.service_helper import ServiceHelper


class YoloProcessing(TableDetectionInterface, TableExtractionInterface):

    def __init__(self):
        super().__init__()
        self.fileHandler = FileHandler()
        self.reader = easyocr.Reader(['en'])
        self.helper = ServiceHelper()

    def __yolo_detect(self, image_name: str):
        # load model
        model = YOLO("foduucom/table-detection-and-extraction")

        # set model parameters
        model.overrides["conf"] = 0.25  # NMS confidence threshold
        model.overrides["iou"] = 0.45  # NMS IoU threshold
        model.overrides["agnostic_nms"] = False  # NMS class-agnostic
        model.overrides["max_det"] = 1000  # maximum number of detections per image

        image_path = os.path.join(PATH_TO_IMGS, image_name)
        image_name_without_suffix = image_name.removesuffix(".png")

        img = np.array(Image.open(image_path))
        img_height, img_width, img_channels = img.shape

        # perform inference
        results = model.predict(image_path)

        # observe results
        render = render_result(model=model, image=image_path, result=results[0])

        ## draw yolo results
        # r = ImageDraw.Draw(render)
        # table_cout = 0
        tables_on_page = []
        for box in results[0].boxes:
            lb = box.data[0].data
            x1, y1, x2, y2 = (int(lb[0].item()), int(lb[1].item()), int(lb[2].item()), int(lb[3].item()))
            table_coords = Point(
                upperLeftX=x1,
                upperLeftY=y1,
                lowerRightX=x2,
                lowerRightY=y2,
            )

            percentage_coords = self.helper.absolute_coords_to_percentage(table_coords, img_width, img_height)

            # cropping
            # cropped_image = img[y1:y2, x1:x2]
            # cropped_image = Image.fromarray(cropped_image)
            # cropped_image.save(PATH_TO_RESULTS + "/" + image_name_without_suffix + "_table-" + str(table_cout) + ".png")
            # table_cout += 1
            tables_on_page.append(percentage_coords)

        return tables_on_page

    def __find_text(self, img):
        ## mser
        min_area = 300
        max_area = 5000
        mser = cv2.MSER.create(min_area=min_area, max_area=max_area)

        # Convert to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # detect regions in gray scale image
        regions, _ = mser.detectRegions(gray)

        data = []
        mask = np.zeros((img.shape[0], img.shape[1], 1), dtype=np.uint8)

        # fill in bboxes of found text => merge letters together to bigger regions => get white rectangles (text location) on black background img
        for p in regions:
            x, y, w, h = cv2.boundingRect(p.reshape(-1, 1, 2))
            cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -2)

        opening_kernel_size = (10, 10)
        opening_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, opening_kernel_size)
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, opening_kernel)

        closing_kernel_size = (11, 5)
        closing_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, closing_kernel_size)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, closing_kernel)

        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            new_bbox = {
                "left": x,
                "top": y,
                "width": w,
                "height": h,
                "text": "",
            }
            data.append(new_bbox)

        if not data:
            raise NoTableException()
        
        df = pandas.DataFrame(data)
        return df
    
    def __find_row_above(self, all_table_rows: list[TableRow], word: TableWord):
        word_y_center = word.get_y_center()
        if word_y_center <= all_table_rows[0].words[0].bbox_y:
            new_row = TableRow()
            new_row.words.append(word)
            all_table_rows.insert(0, new_row)
            return None
        last_row_first_word = all_table_rows[-1].words[0]
        if word_y_center >= (last_row_first_word.bbox_y + last_row_first_word.bbox_height):
            return all_table_rows[-1]

        for row_idx in range(len(all_table_rows)-1):
            row_above = all_table_rows[row_idx]
            row_above_bottom_border = row_above.words[0].bbox_y + row_above.words[0].bbox_height
            row_below = all_table_rows[row_idx+1]
            row_below_upper_border = row_below.words[0].bbox_y

            if row_above_bottom_border <= word_y_center <= row_below_upper_border:
                return row_above
            

    def __find_gaps(self, all_table_rows: list[TableRow], img_width):
        all_gaps = []

        for row in all_table_rows:
            row_gap = []
            if row.line_broken_words:
                for broken_line in row.line_broken_words:
                    for word_idx in range(len(broken_line) - 1):
                        current_word = broken_line[word_idx]
                        next_word = broken_line[word_idx + 1]
                        current_word_x_end = current_word.get_x_end()
                        next_word_x_start = next_word.bbox_x

                        if current_word_x_end < next_word_x_start:
                            # [gap_start, gap_end]
                            gap = [current_word_x_end, next_word_x_start, next_word.bbox_y, current_word.bbox_height]
                            row_gap.append(gap)

                    all_gaps.append(row_gap)
                    row.line_broken_gaps.append(row_gap)
                    row_gap = []

            for word_idx in range(len(row.words)-1):
                current_word = row.words[word_idx]
                next_word = row.words[word_idx+1]
                current_word_x_end = current_word.get_x_end()
                next_word_x_start = next_word.bbox_x

                if current_word_x_end < next_word_x_start:
                    # [gap_start, gap_end]
                    gap = [current_word_x_end, next_word_x_start, next_word.bbox_y, current_word.bbox_height]
                    row_gap.append(gap)

            first_gap, last_gap = row.get_first_and_last_gap(img_width)
            row_gap.append(last_gap)
            row_gap.insert(0, first_gap)

            all_gaps.append(row_gap)
            row.gaps = row_gap

        return all_gaps
    

    def __extract_broken_rows(self, all_table_rows: list[TableRow], img_width: int):
        extracted_rows = []
        for row in all_table_rows:
            extracted_rows.append(row)
            if row.line_broken_words:
                for broken_line_idx in range(len(row.line_broken_words)):
                    broken_row_words = row.line_broken_words[broken_line_idx]
                    broken_row_gaps = row.line_broken_gaps[broken_line_idx]
                    extracted_row = TableRow()
                    extracted_row.words = broken_row_words

                    first_gap, last_gap = extracted_row.get_first_and_last_gap(img_width)
                    extracted_row.gaps = broken_row_gaps
                    extracted_row.gaps.append(last_gap)
                    extracted_row.gaps.insert(0, first_gap)

                    extracted_rows.append(extracted_row)

        return extracted_rows
    

    def __get_cell_text(self, img_to_crop, y_min, y_max, x_min, x_max):
        img_cell_crop = img_to_crop[y_min:y_max, x_min:x_max]
        ocr_results = self.reader.readtext(img_cell_crop)
        text = self.__get_ocr_text(ocr_results)
        return text
    

    def __get_ocr_text(self, ocr_results):
        img_text = ""
        for (bbox, text, prob) in ocr_results:
            img_text = img_text + text
        return img_text

    
    def __split_words_to_rows_and_columns(self, cropped_table_image):
        ext_df = self.__find_text(cropped_table_image)
        ext_df['left_rounded'] = ext_df['left'] // 20
        ext_df = ext_df.sort_values(['left_rounded', 'top'], ascending=[True, True])

        all_table_rows = []
        table_row = TableRow()
        row = ext_df.iloc[0]
        word = TableWord(row)
        table_row.words.append(word)
        all_table_rows.append(table_row)

        # hladanie riadkov
        # kym rastie y-ova suradnica, jedna sa o novy riadok
        # ked pride k nahlemu skoku v y-ovej suradnici (zrazu bude mala, predtym bola velka),
        # sme uz znovu niekde na vrchu tabulky a jedna sa o novy stlpec
        previous_y = row['top']
        idx_start = 1
        for index, row in ext_df[idx_start:].iterrows():
            current_y = row['top']
            if current_y > previous_y:
                table_row = TableRow()
                word = TableWord(row)
                table_row.words.append(word)
                all_table_rows.append(table_row)

                previous_y = current_y
            else:
                break

        # pokracujeme v prechadzani df, hladame, ku ktoremu riadku stlpec patri
        # ak sa y-ovy stred aktualne triediaceho slova nachadza niekde v y-ovom rozsahu zaciatku riadku,
        # je slovo priradene k danemu riadku
        idx_start = len(all_table_rows)
        num_of_broken_lines = 0
        for index, row in ext_df[idx_start:].iterrows():
            word = TableWord(row)
            was_matched_to_row = False
            for table_row in all_table_rows:
                if table_row.has_in_row_range(word):
                    table_row.add_to_words(word)
                    was_matched_to_row = True
            if not was_matched_to_row:
                row_above = self.__find_row_above(all_table_rows, word)
                if row_above is not None:
                    row_above.add_line_broken_words(word)
                    num_of_broken_lines += 1

        image_width = cropped_table_image.shape[1]
        gaps = self.__find_gaps(all_table_rows, image_width)
        extracted_rows = self.__extract_broken_rows(all_table_rows, image_width)

        total_rows = len(extracted_rows)
        spacing_mat = np.zeros((total_rows, image_width), dtype=np.uint8)

        for i in range(0, len(extracted_rows)):
            for gap in extracted_rows[i].gaps:
                spacing_mat[i][gap[0]:gap[1]] = 1

        resulting_columns = spacing_mat.prod(axis=0)
        final_gaps = []
        start = -1
        for i in range(0, len(resulting_columns)):
            if resulting_columns[i] == 1 and start == -1:
                start = i
            elif resulting_columns[i] == 0 and start != -1:
                gap_width = i - start
                gap_middle_point = start + gap_width // 2
                final_gaps.append(gap_middle_point)
                start = -1

        if start != -1:
            gap_width = (image_width-1) - start
            gap_middle_point = start + gap_width // 2
            final_gaps.append(gap_middle_point)

        final_gaps.append(image_width-1)
        if 0 not in final_gaps and 1 not in final_gaps:
            final_gaps.insert(0, 1)

        # connect strings in columns:
        final_table = []
        for row in extracted_rows:
            final_row = []
            for column_gap_idx in range(1, len(final_gaps)):
                current_column = final_gaps[column_gap_idx]
                previous_column = final_gaps[column_gap_idx - 1]

                cell_y_min, cell_y_max = row.get_cell_y_range(current_column, previous_column)
                row_column_content = self.__get_cell_text(np.array(cropped_table_image), cell_y_min, cell_y_max, previous_column, current_column)

                final_row.append(row_column_content)

            final_table.append(final_row)

        return final_table


    def detect_tables(self):
        all_images = self.fileHandler.get_directory_content(PATH_TO_IMGS)
        all_tables_in_doc = {}
        for img_name_with_path in all_images:
            page_number = int(img_name_with_path[img_name_with_path.find('-')+1 : img_name_with_path.find('.')])
            tables_on_page = self.__yolo_detect(img_name_with_path)
            all_tables_in_doc[page_number] = tables_on_page

        return all_tables_in_doc

    def extract_tabular_data(self, rectangle_data: SingleTableRequest):
        # get only table part from page image
        cropped_table_image = self.helper.crop_image(request=rectangle_data)
        # cv2.imwrite(PATH_TO_RESULTS + '/test.png', cropped_table_image)
        result = self.__split_words_to_rows_and_columns(cropped_table_image)
        return result
