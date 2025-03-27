from typing import Annotated
from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status

from src.custom_types.api_types import (
    SingleTableRequest,
    TableDetectionMethod,
    TableDetectionResponse,
    TableExtractionMethod,
    TableExtractionResponse,
)
from src.custom_types.interfaces import TableDetectionInterface, TableExtractionInterface
from src.file_handler import FileHandler
from src.pdf_processing.openai_processing import OpenAiProcessing
from src.pdf_processing.pymu_processing import PymuProcessing
from src.pdf_processing.yolo_processing import YoloProcessing
from src.service.table_detection_service import TableDetectionService
from src.service.table_extraction_service import TableExtractionService

tags = ["PDF"]
pdf_router = APIRouter(prefix="/pdf", tags=tags)


def get_file_handler() -> FileHandler:
    return FileHandler()


def get_yolo_strategy() -> TableDetectionInterface | TableExtractionInterface:
    return YoloProcessing()


def get_pymu_strategy() -> TableDetectionInterface | TableExtractionInterface:
    return PymuProcessing()


def get_openai_strategy() -> TableExtractionInterface:
    return OpenAiProcessing()


def get_table_detection_service(
    pymu_detection: Annotated[TableDetectionInterface, Depends(get_pymu_strategy)],
    yolo_detection: Annotated[TableDetectionInterface, Depends(get_yolo_strategy)],
) -> TableDetectionService:
    return TableDetectionService(pymu_detection=pymu_detection, yolo_detection=yolo_detection)


def get_table_extraction_service(
    pymu_extraction: Annotated[TableExtractionInterface, Depends(get_pymu_strategy)],
    yolo_extraction: Annotated[TableExtractionInterface, Depends(get_yolo_strategy)],
    openai_extraction: Annotated[TableExtractionInterface, Depends(get_openai_strategy)],
) -> TableExtractionService:
    return TableExtractionService(
        pymu_extraction=pymu_extraction, yolo_extraction=yolo_extraction, gpt_extraction=openai_extraction
    )


# upload pdf -> dostane pdf v requeste, vrati len status code
@pdf_router.post("/")
def upload_pdf_file(
    file: UploadFile = File(...),
    pdf_handler: FileHandler = Depends(get_file_handler),
):
    pdf_handler.upload_pdf_file(file)
    return Response(status_code=status.HTTP_201_CREATED)


# get all tables based on detection method -> dostane v requeste detection method, vrati mapu {strana: [tabulky], ...}
@pdf_router.get("/all_tables/{detection_method}", response_model=TableDetectionResponse, status_code=status.HTTP_200_OK)
def get_all_tables(
    detection_method: TableDetectionMethod,
    table_detection_service: Annotated[TableDetectionService, Depends(get_table_detection_service)],
):
    result = table_detection_service.detect_tables(detection_method=detection_method)
    return result


# extract table based on extraction method -> dostane v requeste detection method a bbox, vrati [[riadok tabulky], ...]
@pdf_router.get("/table/{extraction_method}", response_model=TableExtractionResponse, status_code=status.HTTP_200_OK)
def extract_single_table(
    extraction_method: TableExtractionMethod,
    table_extraction_service: Annotated[TableExtractionService, Depends(get_table_extraction_service)],
    pdfPageNumber: int = Query(..., description="PDF page number"),
    upperLeftX: float = Query(..., description="Upper left X coordinate"),
    upperLeftY: float = Query(..., description="Upper left Y coordinate"),
    lowerRightX: float = Query(..., description="Lower right X coordinate"),
    lowerRightY: float = Query(..., description="Lower right Y coordinate"),
):
    rectangle = SingleTableRequest(
        pdf_page_number=pdfPageNumber,
        upper_left_x=upperLeftX,
        upper_left_y=upperLeftY,
        lower_right_x=lowerRightX,
        lower_right_y=lowerRightY,
    )

    result = table_extraction_service.extract_table_data(extraction_method=extraction_method, rectangle_data=rectangle)
    return result
