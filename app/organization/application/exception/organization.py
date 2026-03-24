from core.common.exceptions.base import CustomException


class OrganizationNotFoundException(CustomException):
    code = 404
    error_code = "ORGANIZATION__NOT_FOUND"
    message = "조직을 찾을 수 없습니다."
