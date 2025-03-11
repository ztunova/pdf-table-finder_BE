from abc import ABC, abstractmethod


class TableDetectionInterface(ABC):
    @abstractmethod
    def detect_tables(self):
        pass


class TableDataExtractionInterface(ABC):
    @abstractmethod
    def extract_tabular_data(self):
        pass
