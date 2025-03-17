import os
import numpy as np
from PIL import Image, ImageDraw
import pymupdf
from ultralyticsplus import YOLO, render_result
from src.constants import PATH_TO_IMGS, PATH_TO_PDFS, PATH_TO_RESULTS
from src.custom_types.api_types import Point, SingleTableRequest
from src.custom_types.interfaces import TableExtractionInterface, TableDetectionInterface
from src.file_handler import FileHandler


class YoloProcessing(TableDetectionInterface, TableExtractionInterface):

    def __init__(self):
        super().__init__()
        self.fileHandler = FileHandler()

    def __yolo_detect(self, image_name: str):
        # load model
        model = YOLO("foduucom/table-detection-and-extraction")

        # set model parameters
        model.overrides["conf"] = 0.25  # NMS confidence threshold
        model.overrides["iou"] = 0.45  # NMS IoU threshold
        model.overrides["agnostic_nms"] = False  # NMS class-agnostic
        model.overrides["max_det"] = 1000  # maximum number of detections per image

        image_path = os.path.join(PATH_TO_IMGS, image_name)
        print(image_path)
        image_name_without_suffix = image_name.removesuffix(".png")

        img = np.array(Image.open(image_path))

        # perform inference
        results = model.predict(image_path)

        # observe results
        render = render_result(model=model, image=image_path, result=results[0])

        ## draw yolo results
        r = ImageDraw.Draw(render)
        table_cout = 0
        tables_on_page = []
        for box in results[0].boxes:
            print(box)
            lb = box.data[0].data
            x1, y1, x2, y2 = (int(lb[0].item()), int(lb[1].item()), int(lb[2].item()), int(lb[3].item()))
            print(x1, y1, x2, y2)
            table_coords = Point(
                upperLeftX=x1,
                upperLeftY=y1,
                lowerRightX=x2,
                lowerRightY=y2,
            )

            # cropping
            cropped_image = img[y1:y2, x1:x2]
            cropped_image = Image.fromarray(cropped_image)
            cropped_image.save(PATH_TO_RESULTS + "/" + image_name_without_suffix + "_table-" + str(table_cout) + ".png")
            table_cout += 1
            tables_on_page.append(table_coords)

        return tables_on_page
    
    def __crop_image(self, request: SingleTableRequest):
        image_path = PATH_TO_IMGS + "/page-%i.png" % request.pdf_page_number
        img = np.array(Image.open(image_path))
        cropped_image = img[request.upper_left_y:request.lower_right_y, request.upper_left_x:request.lower_right_x]

        return cropped_image
        # cropped_image = Image.fromarray(cropped_image)
        # cropped_image.save(PATH_TO_RESULTS + "/" + image_name_without_suffix + "_table-" + str(table_cout) + ".png")

    
    # def do_ocr(self, cropped_table_image):
    #     output_dir = results_dir + '/' + pdf_name.removesuffix('.pdf')
    #     if not os.path.exists(output_dir):
    #         os.makedirs(output_dir)
    #     output_file_dir = output_dir + '/' + img_name.removesuffix('.png') + '.xlsx'
    #     img_path = table_imgs_dir + '/' + img_name
    #     print(img_path)

    #     # img_cv2 = cv2.imread(img_path)
    #     # im = Image.open(img_path)
    #     im = cropped_table_image

    #     ext_df = find_text(img_cv2, np.array(im), img_name)
    #     ext_df['left_rounded'] = ext_df['left'] // 20
    #     ext_df = ext_df.sort_values(['left_rounded', 'top'], ascending=[True, True])

    #     all_table_rows = []
    #     table_row = MyTableRow()
    #     row = ext_df.iloc[0]
    #     word = TableWord(row)
    #     table_row.words.append(word)
    #     all_table_rows.append(table_row)

    #     # hladanie riadkov
    #     # kym rastie y-ova suradnica, jedna sa o novy riadok
    #     # ked pride k nahlemu skoku v y-ovej suradnici (zrazu bude mala, predtym bola velka),
    #     # sme uz znovu niekde na vrchu tabulky a jedna sa o novy stlpec
    #     previous_y = row['top']
    #     idx_start = 1
    #     for index, row in ext_df[idx_start:].iterrows():
    #         current_y = row['top']
    #         if current_y > previous_y:
    #             table_row = MyTableRow()
    #             word = TableWord(row)
    #             table_row.words.append(word)
    #             all_table_rows.append(table_row)

    #             previous_y = current_y
    #         else:
    #             break

    #     # pokracujeme v prechadzani df, hladame, ku ktoremu riadku stlpec patri
    #     # ak sa y-ovy stred aktualne triediaceho slova nachadza niekde v y-ovom rozsahu zaciatku riadku,
    #     # je slovo priradene k danemu riadku
    #     idx_start = len(all_table_rows)
    #     num_of_broken_lines = 0
    #     for index, row in ext_df[idx_start:].iterrows():
    #         word = TableWord(row)
    #         was_matched_to_row = False
    #         for table_row in all_table_rows:
    #             if table_row.has_in_row_range(word):
    #                 table_row.add_to_words(word)
    #                 was_matched_to_row = True
    #         if not was_matched_to_row:
    #             row_above = find_row_above(all_table_rows, word)
    #             # row_above.add_to_words(word)
    #             if row_above is not None:
    #                 row_above.add_line_broken_words(word)
    #                 num_of_broken_lines += 1

    #     print_table(all_table_rows)

    #     image_width = im.size[0]
    #     gaps = find_gaps(all_table_rows, image_width)
    #     extracted_rows = extract_broken_rows(all_table_rows, image_width)

    #     # # draw gaps
    #     # for row in extracted_rows:
    #     #     color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #     #
    #     #     for gap in row.gaps:
    #     #             gap_start, gap_end, gap_y, gap_height = gap
    #     #             cv2.rectangle(img_cv2, (gap_start, gap_y), (gap_end, gap_y + gap_height), color, 2)

    #     total_rows = len(extracted_rows) #+ num_of_broken_lines
    #     spacing_mat = np.zeros((total_rows, image_width), dtype=np.uint8)
    #     # print(spacing_mat.shape)

    #     for i in range(0, len(extracted_rows)):
    #         for gap in extracted_rows[i].gaps:
    #             spacing_mat[i][gap[0]:gap[1]] = 1

    #     resulting_columns = spacing_mat.prod(axis=0)
    #     # final_gaps = [1]
    #     final_gaps = []
    #     start = -1
    #     for i in range(0, len(resulting_columns)):
    #         if resulting_columns[i] == 1 and start == -1:
    #             start = i
    #         elif resulting_columns[i] == 0 and start != -1:
    #             gap_width = i - start
    #             gap_middle_point = start + gap_width // 2
    #             final_gaps.append(gap_middle_point)
    #             start = -1

    #     if start != -1:
    #         gap_width = (image_width-1) - start
    #         gap_middle_point = start + gap_width // 2
    #         final_gaps.append(gap_middle_point)

    #     final_gaps.append(image_width-1)
    #     if 0 not in final_gaps and 1 not in final_gaps:
    #         final_gaps.insert(0, 1)

    #     # # draw columns
    #     for gap in final_gaps:
    #         cv2.line(img_cv2, (gap, 0), (gap, 1000), (255, 0, 0), 4)

    #     # connect strings in columns:
    #     final_table = []
    #     for row in extracted_rows:
    #         final_row = []
    #         for column_gap_idx in range(1, len(final_gaps)):
    #             current_column = final_gaps[column_gap_idx]
    #             previous_column = final_gaps[column_gap_idx - 1]

    #             # if current_column == previous_column :
    #             #     continue

    #             # row_column_content = row.get_concat_by_column(current_column, previous_column)

    #             cell_y_min, cell_y_max = row.get_cell_y_range(current_column, previous_column)
    #             row_column_content = get_cell_text(np.array(im), cell_y_min, cell_y_max, previous_column, current_column)
    #             #
    #             color = get_random_color()
    #             cv2.rectangle(img_cv2, (previous_column, cell_y_min), (current_column, cell_y_max), color, 2)
    #             cv2.putText(img_cv2, row_column_content, (previous_column, cell_y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)

    #             final_row.append(row_column_content)
    #         final_table.append(final_row)

    #     # export do excelu
    #     # table_as_df = pandas.DataFrame(final_table)
    #     # table_as_df = table_as_df.replace(r'^\s*$', np.nan, regex=True)
    #     # table_as_df.dropna(how='all', axis=1, inplace=True)
    #     # table_as_df.to_excel(output_file_dir, index=False, header=False)

    #     ## save images with detected text or gaps
    #     cv2.imwrite(test_dir, img_cv2)


    def detect_tables(self):
        all_images = self.fileHandler.get_directory_content(PATH_TO_IMGS)
        all_tables_in_doc = {}
        for img_name_with_path in all_images:
            page_number = int(img_name_with_path[img_name_with_path.find('-')+1 : img_name_with_path.find('.')])
            print('page number: ', page_number)
            tables_on_page = self.__yolo_detect(img_name_with_path)
            all_tables_in_doc[page_number] = tables_on_page

        return all_tables_in_doc

    def extract_tabular_data(self, rectangle_data: SingleTableRequest):
        cropped_table_image = self.__crop_image(request=rectangle_data)
        self.do_ocr(cropped_table_image)
        pass
