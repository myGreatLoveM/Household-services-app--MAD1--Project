from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange

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

