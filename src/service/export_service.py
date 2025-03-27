import io
from typing import Dict
import zipfile
import pandas as pd
from src.custom_types.api_types import ExportTablesRequest


class ExportService:
    def export_to_excel(self, data: ExportTablesRequest):
        data = data.data
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for key, value in data.items():
                sheet_name = value.title.translate({ord(c): " " for c in "[]:*?/\\"})
                table_data = pd.DataFrame(value.extractedData)
                table_data.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

        output.seek(0)
        return output

    def export_to_csv(self, data: ExportTablesRequest):
        data = data.data
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for key, value in data.items():
                csv_buffer = io.BytesIO()

                table_data = pd.DataFrame(value.extractedData)
                table_data.to_csv(csv_buffer, index=False, header=False)
                
                csv_buffer.seek(0)
                
                sanitized_title = value.title.translate({ord(c): "_" for c in "[]:*?/\\"})
                file_name = f"{sanitized_title}.csv"
                zip_file.writestr(file_name, csv_buffer.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer
