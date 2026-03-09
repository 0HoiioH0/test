from core.common.exceptions.base import CustomException


class UserEmailAlreadyExistsException(CustomException):
    code = 400
    error_code = "USER__EMAIL_ALREADY_EXISTS"
    message = "이미 등록된 이메일입니다."
