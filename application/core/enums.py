from enum import Enum

class UserRoleEnum(Enum):
    ADMIN = 'admin'
    PROVIDER = 'provider'
    CUSTOMER = 'customer'


class UserGenderEnum(Enum):
    MALE = 'male'
    FEMALE = 'female'