import numpy as np
import pandas as pd
from src.custom_types.api_types import SingleTableRequest, TableExtractionMethod, TableExtractionResponse
from src.custom_types.interfaces import TableExtractionInterface
from src.exceptions.custom_exceptions import InvalidTableMethodException, NoTableException


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
        if extraction_method not in self.__extraction_strategies:
            raise InvalidTableMethodException(extraction_method)

        strategy = self.__extraction_strategies[extraction_method]
        extracted_table_data = strategy.extract_tabular_data(rectangle_data)
        if not extracted_table_data:
            raise NoTableException(message="No table found withing given coordinates")

        # replace empty/ blank strings with NaN and drop all empty columns and rows
        extracted_data_as_df = pd.DataFrame(extracted_table_data)
        extracted_data_as_df = extracted_data_as_df.replace(r'^\s*$', np.nan, regex=True)
        extracted_data_as_df.dropna(how='all', inplace=True)
        extracted_data_as_df.dropna(how='all', axis=1, inplace=True)
        extracted_data_as_df = extracted_data_as_df.fillna("")
        extracted_table_data = extracted_data_as_df.values.tolist()

        result = TableExtractionResponse(tableData=extracted_table_data)
        return result
