from abc import ABC, abstractmethod


class TableFindingInterface(ABC):
    @abstractmethod
    def get_location_of_tables(self):
        pass


class TableDataExtractionInterface(ABC):
    @abstractmethod
    def extract_tabular_data(self):
        pass
