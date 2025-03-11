from src.custom_types.api_types import SingleTableRequest
from src.custom_types.interfaces import TableExtractionInterface


class OpenAiProcessing(TableExtractionInterface):
    def extract_tabular_data(self, rectangle_data: SingleTableRequest):
        pass
