from typing import Dict, List
from PIL import Image
import numpy as np
from src.constants import PATH_TO_IMGS
from src.custom_types.api_types import Point, SingleTableRequest


class ServiceHelper:
    def crop_image(self, request: SingleTableRequest):
        print('cropping img')
        image_path = PATH_TO_IMGS + "/page-%i.png" % request.pdf_page_number
        img = np.array(Image.open(image_path))
        cropped_image = img[int(request.upper_left_y):int(request.lower_right_y), int(request.upper_left_x):int(request.lower_right_x)]
        return cropped_image
    
    def __get_percentage(self, part, whole):
        return (part / whole) * 100
    
    def coords_to_percentage(self, data: Point, page_width, page_height):
        percentage_coords = Point(
            upperLeftX=self.__get_percentage(data.upperLeftX, page_width),
            upperLeftY=self.__get_percentage(data.upperLeftY, page_height),
            lowerRightX=self.__get_percentage(data.lowerRightX, page_width),
            lowerRightY=self.__get_percentage(data.lowerRightY, page_height),
        )
        return percentage_coords