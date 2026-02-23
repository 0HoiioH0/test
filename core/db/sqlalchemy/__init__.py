from .mapping.user import init_user_mappers
from .mapping.file import init_file_mappers

def init_orm_mappers():
    init_user_mappers()
    init_file_mappers()
