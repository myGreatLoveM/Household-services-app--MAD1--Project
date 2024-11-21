from flask import flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, ValidationError, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from application.admin.models import Category
from application.providers.models import Provider
from .enums import ProviderAvailabilityEnum
from application.extensions import db


class ServiceListingForm(FlaskForm):
    title = StringField(
        label='Title',
        validators=[DataRequired(message='Title is required'), Length(min=3, max=100)],
        render_kw={"placeholder": "Test Service title"}
    )
    price = IntegerField(
        label='Price (in rupees) / hr',
        validators=[DataRequired(message='Price is required'), NumberRange(min=0)],
        render_kw={"placeholder": "price should be above base price"}
    )
    time_required_hr = IntegerField(
        label='Time Required (in hrs)',
        validators=[DataRequired(message='Time is required'), NumberRange(min=1)],
        render_kw={"placeholder": "time required to complete service"}
    )
    availability = SelectField(
        label='Availability',
        choices=[e.value for e in ProviderAvailabilityEnum],
        validators=[DataRequired(message='availbility is required')],
    )
    description = TextAreaField(
        label='Description',
        validators=[DataRequired(message='description is required')],
        render_kw={"placeholder": "What is offered in the service"}
    )

    @property
    def base_price(self):
        # provider = Provider.query.filter_by(id=current_user.provider.id).first()
        base_price = db.session.query(
            Category.base_price
        ).join(Provider, Category.providers).filter_by(id=current_user.provider.id).first()

        return base_price[0]

    @property
    def service_price(self):
        return self.price.data * self.time_required_hr.data

    def validate_price(self, field):
        if field.data < self.base_price:
            flash('Price should be above base price', 'error')
            raise ValidationError('Price should be above base price')
