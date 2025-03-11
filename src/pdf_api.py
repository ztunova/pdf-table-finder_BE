from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status

from src.custom_types.api_types import SingleTableRequest, TableDetectionMethod, TableExtractionMethod
from src.file_handler import FileHandler

tags = ["PDF"]
pdf_router = APIRouter(prefix="/pdf", tags=tags)


def get_file_handler():
    return FileHandler()


# mozno export -> dostane data a format, vrati subors
# upload pdf -> dostane pdf v requeste, vrati len status code
@pdf_router.post("/")
def upload_pdf_file(
    file: UploadFile = File(...),
    pdf_handler: FileHandler = Depends(get_file_handler),
):
    pdf_handler.upload_pdf_file(file)
    return Response(status_code=status.HTTP_201_CREATED)


# get all tables based on detection method -> dostane v requeste detection method, vrati mapu {strana: [tabulky], ...}
@pdf_router.get("/all_tables/{detection_method}")
def get_all_tables(
    detection_method: TableDetectionMethod,
):
    print(detection_method)
    return Response(status_code=status.HTTP_200_OK)


# extract table based on extraction method -> dostane v requeste detection method a bbox, vrati [[riadok tabulky], ...]
@pdf_router.get("/table/{extraction_method}")
def extract_single_table(
    extraction_method: TableExtractionMethod,
    pdfPageNumber: int = Query(..., description="PDF page number"),
    upperLeftX: float = Query(..., description="Upper left X coordinate"),
    upperLeftY: float = Query(..., description="Upper left Y coordinate"),
    lowerRightX: float = Query(..., description="Lower right X coordinate"),
    lowerRightY: float = Query(..., description="Lower right Y coordinate"),
    rectWidth: float = Query(..., description="Rectangle width"),
    rectHeight: float = Query(..., description="Rectangle height"),
):
    rectangle = SingleTableRequest(
        pdf_page_number=pdfPageNumber,
        upper_left_x=upperLeftX,
        upper_left_y=upperLeftY,
        lower_right_x=lowerRightX,
        lower_right_y=lowerRightY,
        rect_width=rectWidth,
        rect_height=rectHeight,
    )
    print(extraction_method)
    print(rectangle)
    return Response(status_code=status.HTTP_200_OK)
