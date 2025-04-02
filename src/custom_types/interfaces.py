from abc import ABC, abstractmethod
from typing import Dict, List

from src.custom_types.api_types import Point, SingleTableRequest


class TableDetectionInterface(ABC):
    @abstractmethod
    def detect_tables(self, pdf_name: str) -> Dict[int, List[Point]]:
        pass


class TableExtractionInterface(ABC):
    @abstractmethod
    def extract_tabular_data(self, pdf_name: str, rectangle_data: SingleTableRequest):
        pass
