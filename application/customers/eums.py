from enum import Enum


# booking confirmations, rejections, cancellations, or rescheduling.
# class BookingStatusEnum(Enum):
#     PENDING = 'pending'
#     CONFIRMED = 'confirmed'
#     REJECTED = 'rejected'
#     COMPLETED = 'completed'
#     CANCELLED = 'cancelled'
#     RESCHEDULE = 'rescheduled'
#     NOT_SHOWN = 'not_shown'


class CustomerPaymentStatusEnum(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'


class CustomerPaymentMethodEnum(Enum):
    CREDIT_CARD = 'credit_card'
    PAYPAL = 'paypal'
    UPI = 'upi'
