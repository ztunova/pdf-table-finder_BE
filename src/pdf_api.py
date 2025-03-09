from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from src.file_handler import FileHandler

tags = ['PDF']
pdf_router = APIRouter(prefix='/pdf', tags=tags)

def get_file_handler():
    return FileHandler()

@pdf_router.post("/")
def upload_pdf_file(
    file: UploadFile = File(...),
    pdf_handler: FileHandler = Depends(get_file_handler)
):
    pdf_handler.upload_pdf_file(file)
    return Response(status_code=status.HTTP_201_CREATED)
