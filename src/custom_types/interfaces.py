from abc import (
    ABC,
    abstractmethod,
)


class TableFindingInterface(ABC):
    @abstractmethod
    def get_location_of_tables(
        self,
        pdf_document,
    ):
        pass


class TableDataExtractionInterface(ABC):
    @abstractmethod
    def extract_tabular_data(
        self,
    ):
        pass
