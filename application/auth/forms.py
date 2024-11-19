from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, PasswordField, SubmitField, BooleanField, RadioField, DateTimeField, TextAreaField, ValidationError, IntegerField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo, ValidationError, InputRequired, NumberRange
from application.admin.models import Category
from application.core.enums import UserGenderEnum


class CustomerRegisterForm(FlaskForm):
    full_name = StringField(
        label='Full Name',
        validators=[DataRequired(
            message='Full name is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "test name"}
    )
    username = StringField(
        label='Username',
        validators=[DataRequired(
            message='Username is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "test username"}
    )
    email = StringField(
        label='Email',
        validators=[DataRequired(message='Email is required'), Email()],
        render_kw={"placeholder": "testuser@gmail.com"}
    )
    gender = SelectField(
        label='Gender',
        choices=['Male', 'Female'],
        validators=[DataRequired(
            message='Gender is required')],
    )
    location = StringField(
        'Location',
        validators=[DataRequired(
            message='Location is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "Rajkot, Gujarat"}
    )
    contact = StringField(
        'Contact ',
        validators=[DataRequired(
            message='Contact is required'), Length(min=10, max=100)],
        render_kw={"placeholder": "9876543210"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(
            message='Password is required'), Length(min=6, max=20)],
        render_kw={"placeholder": "Enter your password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(message='Confirm Password is required'), Length(
            min=6, max=20), EqualTo(fieldname='password', message='passeword dont match')],
        render_kw={"placeholder": "Enter confirm password"}
    )
    submit = SubmitField(
        'Register'
    )


class ProviderRegisterForm(FlaskForm):
    full_name = StringField(
        label='Full Name',
        validators=[DataRequired(
            message='Full name is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "test name"}
    )
    username = StringField(
        label='Username',
        validators=[DataRequired(
            message='Username is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "Test username"}
    )
    email = StringField(
        label='Email',
        validators=[DataRequired(message='Email is required'), Email()],
        render_kw={"placeholder": "testuser@gmail.com"}
    )
    gender = SelectField(
        label='Gender',
        choices=[g.value for g in UserGenderEnum],
        validators=[DataRequired(
            message='Gender is required')],
        render_kw={"placeholder": "experience in yrs"}
    )
    category = SelectField(
        label='Category',
        choices=[],
        validators=[DataRequired(
            message='Category is required')],
        render_kw={"placeholder": "Categories"}
    )
    experience = IntegerField(
        'Experience (in yrs)',
        validators=[DataRequired(
            message='Experience is required'), NumberRange(min=0, max=50)],
        render_kw={"placeholder": "experience in yrs"}
    )
    location = StringField(
        'Location',
        validators=[DataRequired(
            message='Location is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "Rajkot, Gujarat"}
    )
    contact = StringField(
        'Contact ',
        validators=[DataRequired(
            message='Contact is required'), Length(min=10, max=100)],
        render_kw={"placeholder": "9876543210"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(
            message='Password is required'), Length(min=6, max=20)],
        render_kw={"placeholder": "Enter your password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(message='Confirm Password is required'), Length(
            min=6, max=20), EqualTo(fieldname='password', message='password dont match')],
        render_kw={"placeholder": "Enter confirm password"}
    )
    submit = SubmitField(
        'Register'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.query.all()
        cat_names = [category.name for category in categories]
        self.category.choices = cat_names


class LoginForm(FlaskForm):
    username = StringField(
        label='Username',
        validators=[DataRequired(
            message='Username is required'), Length(min=3, max=30)],
        render_kw={"placeholder": "test username"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(
            message='Password is required'), Length(min=6, max=20)],
        render_kw={"placeholder": "Enter your password"}
    )
    submit = SubmitField(
        'Login'
    )
