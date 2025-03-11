from abc import ABC, abstractmethod


class TableDetectionInterface(ABC):
    @abstractmethod
    def detect_tables(self):
        pass


class TableExtractionInterface(ABC):
    @abstractmethod
    def extract_tabular_data(self):
        pass
