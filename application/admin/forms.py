from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, PasswordField, SubmitField, BooleanField, RadioField, DateTimeField, TextAreaField, ValidationError, IntegerField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo, ValidationError, InputRequired, NumberRange
from application.admin.models import Category



class CategoryRegisterForm(FlaskForm):
    name = StringField(
        label='Name',
        validators=[DataRequired(message='category name is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "test category name"}
    )
    base_price = IntegerField(
        'Base Price (in ₹)',
        validators=[DataRequired(message='Experience is required'), NumberRange(min=50, max=1000)],
        render_kw={"placeholder": "100 ₹"} 
    )
    min_time_hr = IntegerField(
        'Min time required (in hr)',
        validators=[DataRequired(message='min time is required'), NumberRange(min=1, max=5)],
        render_kw={"placeholder": "1 hr"} 
    )
    service_rate = IntegerField(
        'Service rate (in %)',
        validators=[DataRequired(message='service rate is required'), NumberRange(min=1, max=100)],
        render_kw={"placeholder": "% of booking price from providers"} 
    )
    booking_rate = IntegerField(
        'Booking rate (in %)',
        validators=[DataRequired(message='booking rate is required'), NumberRange(min=1, max=100)],
        render_kw={"placeholder": "% of booking price from customer"} 
    )
    transaction_rate = IntegerField(
        'Transaction rate (in %)',
        validators=[DataRequired(message='transaction rate is required'), NumberRange(min=1, max=100)],
        render_kw={"placeholder": "% of booking price from customer for transaction"}  
    )
    cancellation_rate = IntegerField(
        'Cancellation rate (in %)',
        validators=[DataRequired(message='cancellation rate is required'), NumberRange(min=1, max=100)],
        render_kw={"placeholder": "% of booking price from customer for cancellation"}  
    )
    penalty_rate = IntegerField(
        'Penalty rate (in %)',
        validators=[DataRequired(message='penalty rate is required'), NumberRange(min=1, max=100)],
        render_kw={"placeholder": "% of booking price from provider for cancellation"}  
    )
    description = TextAreaField(
        label='Description',
        validators=[DataRequired(message='category description is required')],
        render_kw={"placeholder": "What is about the category"}
    )
    submit = SubmitField(
        'Register'
    )

