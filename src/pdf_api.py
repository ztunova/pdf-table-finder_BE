from typing import Annotated, Optional
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
@pdf_router.post("/upload")
def upload_pdf_file(
    file: UploadFile = File(...),
    pdf_handler: FileHandler = Depends(get_file_handler),
):
    """
    Upload new PDF file
    """
    pdf_handler.upload_pdf_file(file)
    return Response(status_code=status.HTTP_201_CREATED)


# get all tables based on detection method -> dostane v requeste detection method, vrati mapu {strana: [tabulky], ...}
@pdf_router.get(
    "/{pdf_name}/all_tables/{detection_method}", response_model=TableDetectionResponse, status_code=status.HTTP_200_OK
)
def get_all_tables(
    pdf_name: str,
    detection_method: TableDetectionMethod,
    table_detection_service: Annotated[TableDetectionService, Depends(get_table_detection_service)],
):
    """
    Detect/ find tables in PDF file. Returns a list of table bounding boxes per each page of file.
    NOTE: All coordinates in response represents percentage - they are relative to page width and height
    """

    result = table_detection_service.detect_tables(pdf_name=pdf_name, detection_method=detection_method)
    return result


# extract table based on extraction method -> dostane v requeste detection method a bbox, vrati [[riadok tabulky], ...]
@pdf_router.get(
    "/{pdf_name}/table/{extraction_method}", response_model=TableExtractionResponse, status_code=status.HTTP_200_OK
)
def extract_single_table(
    pdf_name: str,
    extraction_method: TableExtractionMethod,
    table_extraction_service: Annotated[TableExtractionService, Depends(get_table_extraction_service)],
    pdfPageNumber: int = Query(..., description="PDF page number"),
    upperLeftX: float = Query(..., description="Upper left X coordinate"),
    upperLeftY: float = Query(..., description="Upper left Y coordinate"),
    lowerRightX: float = Query(..., description="Lower right X coordinate"),
    lowerRightY: float = Query(..., description="Lower right Y coordinate"),
    customPrompt: Optional[str] = Query(None, description="Custom prompt for ChatGPT extraction method"),
):
    """
    Extract tabular data within given bounding box.
    NOTE: All coordinates in both request and response are handled as percentage - relative to page width and height
    """

    rectangle = SingleTableRequest(
        pdf_page_number=pdfPageNumber,
        upper_left_x=upperLeftX,
        upper_left_y=upperLeftY,
        lower_right_x=lowerRightX,
        lower_right_y=lowerRightY,
        custom_prompt=customPrompt,
    )

    result = table_extraction_service.extract_table_data(
        pdf_name=pdf_name, extraction_method=extraction_method, rectangle_data=rectangle
    )
    return result


@pdf_router.delete("/{pdf_name}")
def delete_pdf(
    pdf_name: str,
    pdf_handler: FileHandler = Depends(get_file_handler),
):
    """
    Delete all resources related with given PDF (PDF file and all images from conversion)
    """
    pdf_handler.clean_up_pdf(pdf_name=pdf_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
