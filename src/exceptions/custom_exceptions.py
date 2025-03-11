from fastapi import HTTPException, status


class NotAPdfFileException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Uploaded file must be .pdf"
