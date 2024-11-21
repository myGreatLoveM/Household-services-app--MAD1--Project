from datetime import datetime
from flask import flash
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Optional, NumberRange, ValidationError

from application.customers.eums import CustomerPaymentMethodEnum


class BookingForm(FlaskForm):
    book_date = DateField(
        label='Book Date',
        validators=[DataRequired(
            message='Booking dat is required')],
    )
    fullfillment_date = DateField(
        label='Fullfillment Date',
        validators=[DataRequired(
            message='Fullfillment date is required')]
    )
    remark = TextAreaField(
        label='Remarks',
        validators=[DataRequired(
            message='Fullfillment date is required')], 
        render_kw={"placeholder": "Specific requirements or instructions for service provide"}
    )

    def validate_book_date(self, field):
        if field.data < datetime.today().date():
            flash('booking date is incorrect', category='error')
            raise ValidationError('booking date should be in the future')
    
    def validate_fullfillment_date(self, field):
        if field.data < datetime.today().date() or field.data < self.book_date.data:
            flash('fullfillment date is incorrect', category='error')
            raise ValidationError('fullfillment date should be in the future')


class CustomerPaymentForm(FlaskForm):
    method = SelectField(
        label='Payment Method',
        choices=[e.value for e in CustomerPaymentMethodEnum],
        validators=[DataRequired(message='method is required')],
    )


class ReviewForm(FlaskForm):
    rating = IntegerField(
        label='Review',
        validators=[DataRequired(
            message='Experience is required'), NumberRange(min=1, max=5)],
        render_kw={"placeholder": "provide rating here"}
    )
    comment = TextAreaField(
        label='Review',
        validators=[DataRequired(
            message='Review is required')], 
        render_kw={"placeholder": "write your review here"}
    )

    def validate_rating(self, field):
        if field.data > 5:
            flash('rating should be less than 6', category='error')
            raise ValidationError('Please select between 1 to 5 rating')








