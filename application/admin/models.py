from datetime import datetime
from application.extensions import db


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    categories = db.relationship('Category', lazy='dynamic')


class Category(db.Model):
    """
    Category model for organizing services into different types (e.g., Cleaning, Plumbing).
    Helps users to filter and search services more effectively.
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    name = db.Column(db.String(30), unique=True, nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    min_time_hr = db.Column(db.Integer, default=1)
    service_rate = db.Column(db.Integer, nullable=False)
    booking_rate = db.Column(db.Integer, nullable=False)
    transaction_rate = db.Column(db.Integer, nullable=False)
    short_description = db.Column(db.Text)
    long_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    providers = db.relationship('Provider', back_populates='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'
