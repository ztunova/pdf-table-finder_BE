import os
import numpy as np
from PIL import Image, ImageDraw
import pymupdf
from ultralyticsplus import YOLO, render_result
from src.constants import PATH_TO_IMGS, PATH_TO_PDFS, PATH_TO_RESULTS
from src.custom_types.api_types import Point
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
                upper_left_x=x1,
                upper_left_y=y1,
                lower_right_x=x2,
                lower_right_y=y2,
            )

            # cropping
            cropped_image = img[y1:y2, x1:x2]
            cropped_image = Image.fromarray(cropped_image)
            cropped_image.save(PATH_TO_RESULTS + "/" + image_name_without_suffix + "_table-" + str(table_cout) + ".png")
            table_cout += 1
            tables_on_page.append(table_coords)

        return tables_on_page

    def detect_tables(self):
        all_images = self.fileHandler.get_directory_content(PATH_TO_IMGS)
        all_tables_in_doc = {}
        for img_name_with_path in all_images:
            page_number = int(img_name_with_path[img_name_with_path.find('-')+1 : img_name_with_path.find('.')])
            print('page number: ', page_number)
            tables_on_page = self.__yolo_detect(img_name_with_path)
            all_tables_in_doc[page_number] = tables_on_page

        return all_tables_in_doc

    def extract_tabular_data(self):
        pass
