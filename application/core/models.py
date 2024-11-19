from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash
from datetime import datetime
from typing import List

from application.extensions import db
from application.core.enums import UserGenderEnum, UserRoleEnum


class User(db.Model, UserMixin):
    """
    User model to store user information.
    Includes roles to distinguish between admin, service professionals, and customers.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    updated_at = db.Column(db.DateTime(), default=datetime.now, onupdate=datetime.now)

    admin = db.relationship('Admin', uselist=False)
    provider = db.relationship('Provider', back_populates='user', uselist=False)
    customer = db.relationship('Customer', back_populates='user', uselist=False)
    profile = db.relationship('Profile', uselist=False)

    @property
    def is_admin(self):
        return self.role == UserRoleEnum.ADMIN.value
    
    @property
    def is_provider(self):
        return self.role == UserRoleEnum.PROVIDER.value
    
    @property
    def is_customer(self):
        return self.role == UserRoleEnum.CUSTOMER.value
    
    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_name(cls, username) -> "User":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id) -> "User":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["User"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'


class Profile(db.Model):
    """
    Profile model for storing additional information about users.
    Related to the User model using a one-to-one relationship.
    """
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    contact = db.Column(db.String(20))
    bio = db.Column(db.String(100))
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(), default=datetime.now)
    updated_at = db.Column(db.DateTime(), default=datetime.now, onupdate=datetime.now)

    @property
    def avatar(self):
        if self.gender == UserGenderEnum.FEMALE.value:
            return f"https://avatar.iran.liara.run/public/girl?username={self.full_name}"
        return f"https://avatar.iran.liara.run/public/boy?username={self.full_name}"

    def __repr__(self):
        return f'<Profile {self.full_name}>'


