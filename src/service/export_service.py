import io
from typing import Dict
import pandas as pd
from src.constants import PATH_TO_RESULTS
from src.custom_types.api_types import ExportFormat, ExportTablesRequest, TableData


class ExportService:
    def __export_to_excel(self, data: Dict[str, TableData]):
        filename = PATH_TO_RESULTS + "/test.xlsx"
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for key, value in data.items():
                sheet_name = value.title
                sanitized_sheet_name = sheet_name.translate({ord(c): " " for c in "[]:*?/\\"})
                print(sheet_name)
                table_data = pd.DataFrame(value.extractedData)
                table_data.to_excel(writer, sheet_name=sanitized_sheet_name, index=False, header=False)

        output.seek(0)
        return output

    def __export_to_csv(self, data: Dict[str, TableData]):
        pass

    def export_data_to_file(self, export_format: ExportFormat, data: ExportTablesRequest):
        data = data.data
        if (export_format == ExportFormat.EXCEL):
            return self.__export_to_excel(data)
        elif (export_format == ExportFormat.CSV):
            self.__export_to_csv(data)

