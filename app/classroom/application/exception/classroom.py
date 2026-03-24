from core.common.exceptions.base import CustomException


class ClassroomNotFoundException(CustomException):
    code = 404
    error_code = "CLASSROOM__NOT_FOUND"
    message = "강의실을 찾을 수 없습니다."


class ClassroomCodeAlreadyExistsException(CustomException):
    code = 409
    error_code = "CLASSROOM__CODE_ALREADY_EXISTS"
    message = "이미 사용 중인 강의실 코드입니다."
