from datetime import datetime
from application.core.models import Profile, User
from application.extensions import db
from sqlalchemy.ext.hybrid import hybrid_property


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    is_blocked = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', back_populates='customer')
    bookings = db.relationship('Booking', back_populates='customer', lazy='dynamic')

    @hybrid_property
    def username(self):
        return self.user.username
    
    @hybrid_property
    def full_name(self):
        return self.user.profile.full_name


class Booking(db.Model):
    """
    Booking model to handle service bookings by customers.
    Links a customer with a service and manages the status and timing of the booking.
    """
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey(
        'services.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending', 'confirmed', 'reject', 'completed', 'closed'
    book_date = db.Column(db.DateTime)
    fullfillment_date = db.Column(db.DateTime)
    confimation_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    closed_date = db.Column(db.DateTime)
    remark = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    service = db.relationship('Service', back_populates='bookings')
    customer = db.relationship('Customer', back_populates='bookings')
    payment = db.relationship('CustomerPayment', back_populates='booking', uselist=False)
    review = db.relationship('Review', back_populates='booking', uselist=False)


class CustomerPayment(db.Model):
    """
    Payment model to track payments for services booked through the application.
    Includes details about the transaction, status, and associated booking.
    """
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'paid', 'pending', 'cancelled'
    amount = db.Column(db.Integer, nullable=False)
    service_fee = db.Column(db.Integer,  default=0)
    platform_fee = db.Column(db.Integer, default=0)
    transaction_fee = db.Column(db.Integer, default=0)
    discount = db.Column(db.Integer, default=0)
    method = db.Column(db.String(20)) 

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    booking = db.relationship('Booking', back_populates='payment')


    @hybrid_property
    def total_amount(self):
        return self.amount + self.platform_fee + self.transaction_fee - self.discount

    def calculate_final_amount(self):
        return round(self.amount + self.platform_fee + self.transaction_fee - self.discount, 2)

    @hybrid_property
    def final_provider_amount(self):
        return self.amount - self.service_fee
    
    @hybrid_property
    def final_admin_amount(self):
        return self.service_fee + self.platform_fee + self.transaction_fee



class Review(db.Model):
    """
    Review model for customers to leave reviews and ratings for services they have used.
    Helps maintain quality and provide feedback to service professionals.
    """
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey(
        'bookings.id'), nullable=False)
    rating = db.Column(db.Integer, default=5)  # Rating out of 5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    booking = db.relationship('Booking', back_populates='review')



# class Refund(db.Model):
#     __tablename__ = 'refunds'

#     id = db.Column(db.Integer, primary_key=True)
#     booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
#     transaction_id = db.Column(db.Integer, db.ForeignKey(CustomerPayment.id), nullable=False)
#     amount = db.Column(db.Float, nullable=False)  # Amount to be refunded
#     status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Processed', 'Failed'
#     cancellation_charge = db.Column(db.Integer, default=0) # for customer cancellation
#     penalty = db.Column(db.Integer, default=0) # penalty on provider cancellation
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

#     booking = db.relationship('Booking', back_populates='refund')
