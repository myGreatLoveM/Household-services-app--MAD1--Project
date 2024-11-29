from datetime import datetime
from flask_restful import reqparse

def timestamp(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError as e:
        print(e)
        raise ValueError(f"Invalid timestamp format: {value}. Expected format: YYYY-MM-DD")

# category
category_create_parser = reqparse.RequestParser()
category_create_parser.add_argument('name', type=str, required=True, trim=True)
category_create_parser.add_argument('base_price', type=int, required=True)
category_create_parser.add_argument('service_rate', type=int, required=True)
category_create_parser.add_argument('booking_rate', type=int, required=True)
category_create_parser.add_argument('transaction_rate', type=int, required=True)
category_create_parser.add_argument('short_description', type=str, nullable=True)
category_create_parser.add_argument('long_description', type=str, nullable=True)


# service
service_status_parser = reqparse.RequestParser()
service_status_parser.add_argument('status', type=str, location='args', choices=['active', 'pending', 'blocked', 'discontinue'], help='')

service_create_parser = reqparse.RequestParser()
service_create_parser.add_argument('title', type=str, trim=True, required=True)
service_create_parser.add_argument('price', type=int, required=True)
service_create_parser.add_argument('time_required_hr', type=int, required=True, help='time requied')
service_create_parser.add_argument('description', type=str, trim=True, nullable=False)


# booking
booking_status_parser = reqparse.RequestParser()
booking_status_parser.add_argument('status', type=str, location='args', choices=['pending', 'confirmed', 'rejected', 'active', 'completed', 'closed'], nullable=True)

booking_create_parser = reqparse.RequestParser()
booking_create_parser.add_argument('service_id', type=int, required=True, help='service_id is required')
booking_create_parser.add_argument('book_date', type=timestamp, required=True, help='Timestamp in format YYYY-MM-DD and required')
booking_create_parser.add_argument('fullfillment_date', type=timestamp, required=True, help='Timestamp in format YYYY-MM-DD and required')
booking_create_parser.add_argument('remark', type=str, nullable=True)