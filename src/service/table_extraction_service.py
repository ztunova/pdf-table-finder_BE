from src.custom_types.api_types import SingleTableRequest, TableExtractionMethod, TableExtractionResponse
from src.custom_types.interfaces import TableExtractionInterface
from src.exceptions.custom_exceptions import InvalidTableMethod


class TableExtractionService:
    def __init__(
        self,
        pymu_extraction: TableExtractionInterface,
        yolo_extraction: TableExtractionInterface,
        gpt_extraction: TableExtractionInterface,
    ):
        self.__extraction_strategies = {
            TableExtractionMethod.PYMU: pymu_extraction,
            TableExtractionMethod.YOLO: yolo_extraction,
            TableExtractionMethod.CHATGPT: gpt_extraction,
        }

    def extract_table_data(self, extraction_method: TableExtractionMethod, rectangle_data: SingleTableRequest):
        print(extraction_method)
        print(rectangle_data)
        if extraction_method not in self.__extraction_strategies:
            raise InvalidTableMethod(extraction_method)

        strategy = self.__extraction_strategies[extraction_method]
        extracted_table_data = strategy.extract_tabular_data(rectangle_data)
        result = TableExtractionResponse(table_data=extracted_table_data)
        print(result)
        return result
