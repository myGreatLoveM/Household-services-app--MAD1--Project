from enum import Enum


class CustomerPaymentStatusEnum(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'


class CustomerPaymentMethodEnum(Enum):
    CREDIT_CARD = 'credit_card'
    PAYPAL = 'paypal'
    UPI = 'upi'
