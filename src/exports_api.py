from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from src.custom_types.api_types import ExportTablesRequest
from src.service.export_service import ExportService


tags = ["Exports"]
exports_router = APIRouter(prefix="/exports", tags=tags)


def get_export_service() -> ExportService:
    return ExportService()


@exports_router.post("/{pdf_name}/excel", status_code=status.HTTP_200_OK)
def export_to_file(
    pdf_name: str,
    data: ExportTablesRequest,
    export_service: ExportService = Depends(get_export_service),
):
    output = export_service.export_to_excel(data=data)
    pdf_name_without_extension = pdf_name.removesuffix(".pdf")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={pdf_name_without_extension}.xlsx"},
    )


@exports_router.post("/{pdf_name}/csv", status_code=status.HTTP_200_OK)
def export_to_file(
    pdf_name: str,
    data: ExportTablesRequest,
    export_service: ExportService = Depends(get_export_service),
):
    output = export_service.export_to_csv(data=data)
    pdf_name_without_extension = pdf_name.removesuffix(".pdf")
    return StreamingResponse(
        output,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={pdf_name_without_extension}.zip"},
    )
