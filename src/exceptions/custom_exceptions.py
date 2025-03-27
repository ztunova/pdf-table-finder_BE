from fastapi import HTTPException, status


class NotAPdfFileException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Uploaded file must be .pdf"


class InvalidTableMethodException(HTTPException):
    def __init__(self, detection_method):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Unsupported detection method: {detection_method}"


class NoTableException(HTTPException):
    def __init__(self, message):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = message
