from enum import Enum

class UserStatusEnum(Enum):
    APPROVE = 'approve'
    BLOCK = 'block'
    UNBLOCK = 'unblock'


class ServiceStatusEnum(Enum):
    APPROVE = 'approve'
    BLOCK = 'block'
    UNBLOCK = 'unblock'
    DISCONTINUE = 'discontinue'
    CONTINUE = 'continue'
