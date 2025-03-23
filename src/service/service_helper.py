from typing import Dict, List
from PIL import Image
import numpy as np
from src.constants import PATH_TO_IMGS
from src.custom_types.api_types import Point, SingleTableRequest


class ServiceHelper:
    # receives percentage coords
    def crop_image(self, request: SingleTableRequest):
        print('cropping img')
        image_path = PATH_TO_IMGS + "/page-%i.png" % request.pdf_page_number
        img = np.array(Image.open(image_path))
        img_height, img_width, img_channels = img.shape
        absolute_coords = self.percentage_coords_to_absolute(request, img_width, img_height)
        cropped_image = img[int(absolute_coords.upper_left_y):int(absolute_coords.lower_right_y), int(absolute_coords.upper_left_x):int(absolute_coords.lower_right_x)]
        return cropped_image
    
    def __get_percentage(self, part, whole):
        return (part / whole) * 100
    
    def __get_absolute_part(self, percentage, whole):
        return (percentage * whole) / 100
    
    def absolute_coords_to_percentage(self, data: Point, page_width, page_height):
        percentage_coords = Point(
            upperLeftX=self.__get_percentage(data.upperLeftX, page_width),
            upperLeftY=self.__get_percentage(data.upperLeftY, page_height),
            lowerRightX=self.__get_percentage(data.lowerRightX, page_width),
            lowerRightY=self.__get_percentage(data.lowerRightY, page_height),
        )
        return percentage_coords
    
    def percentage_coords_to_absolute(self, data: SingleTableRequest, page_width, page_height):
        absolute_coords = SingleTableRequest(
            pdf_page_number=data.pdf_page_number,
            upper_left_x=self.__get_absolute_part(data.upper_left_x, page_width),
            upper_left_y=self.__get_absolute_part(data.upper_left_y, page_height),
            lower_right_x=self.__get_absolute_part(data.lower_right_x, page_width),
            lower_right_y=self.__get_absolute_part(data.lower_right_y, page_height),
        )
        return absolute_coords