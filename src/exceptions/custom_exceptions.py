from fastapi import HTTPException, status


class NotAPdfFileException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Uploaded file must be .pdf"

class InvalidDetectionMethod(HTTPException):
    def __init__(self, detection_method):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Unsupported detection method: {detection_method}"
