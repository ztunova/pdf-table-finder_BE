import os
import numpy as np
from PIL import Image, ImageDraw
import pymupdf
from ultralyticsplus import YOLO, render_result
from src.constants import PATH_TO_IMGS, PATH_TO_PDFS, PATH_TO_RESULTS
from src.custom_types.interfaces import TableExtractionInterface, TableDetectionInterface
from src.file_handler import FileHandler


class YoloProcessing(TableDetectionInterface, TableExtractionInterface):

    def __init__(self):
        super().__init__()
        self.fileHandler = FileHandler()

    def __yolo_detect__(self, image_name: str):
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
        for box in results[0].boxes:
            print(box)
            lb = box.data[0].data
            x1, y1, x2, y2 = (int(lb[0].item()), int(lb[1].item()), int(lb[2].item()), int(lb[3].item()))
            r.rectangle(
                (int(lb[0].item()), int(lb[1].item()), int(lb[2].item()), int(lb[3].item())), outline=(255, 255, 0)
            )

            # cropping
            cropped_image = img[y1:y2, x1:x2]
            cropped_image = Image.fromarray(cropped_image)
            cropped_image.save(PATH_TO_RESULTS + "/" + image_name_without_suffix + "_table-" + str(table_cout) + ".png")
            table_cout += 1

        return table_cout

    def detect_tables(self):
        return "yolo detect tables"
        all_images = self.fileHandler.get_directory_content(PATH_TO_IMGS)
        for img in all_images:
            self.__yolo_detect__(img)

    def extract_tabular_data(self):
        pass
