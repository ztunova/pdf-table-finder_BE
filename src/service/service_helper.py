from PIL import Image
import numpy as np
from src.constants import PATH_TO_IMGS
from src.custom_types.api_types import SingleTableRequest


class ServiceHelper:
    def crop_image(self, request: SingleTableRequest):
        print('cropping img')
        image_path = PATH_TO_IMGS + "/page-%i.png" % request.pdf_page_number
        img = np.array(Image.open(image_path))
        cropped_image = img[int(request.upper_left_y):int(request.lower_right_y), int(request.upper_left_x):int(request.lower_right_x)]
        return cropped_image