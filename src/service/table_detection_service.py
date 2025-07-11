from src.custom_types.api_types import TableDetectionMethod, TableDetectionResponse
from src.custom_types.interfaces import TableDetectionInterface
from src.exceptions.custom_exceptions import InvalidTableMethodException, NoTableException


class TableDetectionService:
    def __init__(self, pymu_detection: TableDetectionInterface, yolo_detection: TableDetectionInterface):
        self.__detection_strategies = {
            TableDetectionMethod.PYMU: pymu_detection,
            TableDetectionMethod.YOLO: yolo_detection,
        }

    def detect_tables(self, pdf_name: str, detection_method: TableDetectionMethod):
        if detection_method not in self.__detection_strategies:
            raise InvalidTableMethodException(detection_method)

        strategy = self.__detection_strategies[detection_method]
        detected_tables = strategy.detect_tables(pdf_name=pdf_name)
        result = TableDetectionResponse(tables=detected_tables)

        for key, value in result.tables.items():
            if value:
                return result

        raise NoTableException(message="No tables found in file")
