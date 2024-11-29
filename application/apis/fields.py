from flask_restful import fields
from collections import OrderedDict


booking_fields = OrderedDict([
    ('id', fields.Integer),
    ('customer_id', fields.Integer),
    ('service_id', fields.Integer),
    ('status', fields.String),
    ('book_date', fields.DateTime),
    ('fullfillment_date', fields.DateTime),
    ('confimation_date', fields.DateTime),
    ('completed_date', fields.DateTime),
    ('closed_date', fields.DateTime),
    ('created_at', fields.DateTime)
])

customer_fields = OrderedDict([
    ('id', fields.Integer),
    ('user_id', fields.Integer),
    ('is_blocked', fields.Boolean),
])

service_fields = OrderedDict([
    ('id', fields.Integer),
    ('is_approved', fields.Boolean),
    ('is_active', fields.Boolean),
    ('is_blocked', fields.Boolean),
    ('provider_id', fields.Integer),
    ('title', fields.String),
    ('price', fields.Integer),
    ('time_required_hr', fields.Integer),
    ('visibility', fields.String),
    ('availability', fields.String),
    ('description', fields.String),
    ('approved_at', fields.DateTime),
    ('created_at', fields.DateTime),
])

profile_fields = OrderedDict([
    ('full_name', fields.String),
    ('age', fields.Integer),
    ('gender', fields.String),
    ('email', fields.String),
    ('location', fields.String),
    ('contact', fields.String),
])

user_fields = OrderedDict([
    ('id', fields.Integer),
    ('username', fields.String),
    ('role', fields.String),
    ('created_at', fields.DateTime),
    ('profile', fields.Nested(profile_fields))
])

provider_fields = OrderedDict([
    ('id', fields.Integer),
    ('user_id', fields.Integer),
    ('experience', fields.Integer),
    ('wallet', fields.Integer),
    ('user', fields.Nested(user_fields)),
])

category_fields = OrderedDict([
    ('id', fields.Integer),
    ('name', fields.String),
    ('base_price', fields.Integer),
    ('providers', fields.List(fields.Nested(provider_fields)))
])