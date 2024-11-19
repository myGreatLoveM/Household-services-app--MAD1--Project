from enum import Enum


class ProviderAvailabilityEnum(Enum):
    WEEKDAYS = 'weekdays'
    WEEKENDS = 'weekends'
    ALL_TIME = '24/7'


class BookingStatusEnum(Enum):
    PENDING = 'pending'
    CONFIRM = 'confirmed'
    REJECT = 'rejected'
    ACTIVE = 'active'
    COMPLETE = 'completed'
    CLOSE = 'closed'


class ServiceStatusEnum(Enum):
    APPROVE = 'approve'
    BLOCK = 'block'
    UNBLOCK = 'unblock'
    DISCONTINUE = 'discontinue'
    CONTINUE = 'continue'





