from datetime import datetime

from sqlalchemy import UniqueConstraint
from application.extensions import db
from sqlalchemy.ext.hybrid import hybrid_property

from application.providers.enums import ProviderAvailabilityEnum


class Provider(db.Model):
    __tablename__ = 'providers'

    id = db.Column(db.Integer, primary_key=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_providers_user_id'), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', name='fk_providers_category_id'), nullable=False)
    experience = db.Column(db.Integer, default=0)
    wallet = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    approved_at = db.Column(db.DateTime)

    __table_args__ = (
        UniqueConstraint('user_id', name='uq_providers_user_id'),
    )

    user = db.relationship('User', back_populates='provider')
    category = db.relationship('Category', back_populates='providers')  
    services = db.relationship('Service', back_populates='provider', lazy='dynamic')

    @hybrid_property
    def username(self):
        return self.user.username

class Service(db.Model):
    """
    Service model for storing details about services provided by professionals.
    Each service is linked to a service providers who provides it.
    """
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time_required_hr = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(20), default='normal')  # 'normal', 'featured'
    availability = db.Column(db.String(50), default=ProviderAvailabilityEnum.ALL_TIME.value)  # e.g., 'Weekdays', 'Weekends', '24/7'
    description = db.Column(db.String(100))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    approved_at = db.Column(db.DateTime)

    provider = db.relationship('Provider', back_populates='services')
    bookings = db.relationship('Booking', back_populates='service', lazy='dynamic')

    @hybrid_property
    def category(self):
        return self.provider.category

    @hybrid_property
    def avg_rating(self):
        return 5
    
    @hybrid_property
    def no_of_reviews(self):
        return 10