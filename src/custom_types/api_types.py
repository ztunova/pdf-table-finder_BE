from enum import Enum
from typing import Dict, List, Tuple
from pydantic import BaseModel


class Point(BaseModel):
    upperLeftX: float
    upperLeftY: float
    lowerRightX: float
    lowerRightY: float


class TableDetectionResponse(BaseModel):
    tables: Dict[int, List[Point]]


class TableExtractionResponse(BaseModel):
    tableData: List[List[str]]


class SingleTableRequest(BaseModel):
    pdf_page_number: int
    upper_left_x: float
    upper_left_y: float
    lower_right_x: float
    lower_right_y: float
    # rect_width: float
    # rect_height: float


class TableDetectionMethod(str, Enum):
    PYMU = "pymu"
    YOLO = "yolo"


class TableExtractionMethod(str, Enum):
    PYMU = "pymu"
    YOLO = "yolo"
    CHATGPT = "chatgpt"
