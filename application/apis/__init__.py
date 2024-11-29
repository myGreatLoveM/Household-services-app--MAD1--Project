from flask import Blueprint
from flask_restful import Api


api_bp = Blueprint('api_bp', __name__)

api = Api(api_bp)

from .resources import CategoryAPI, CategoryListAPI, CustomerBookingAPI, CustomerBookingListAPI, ProviderServiceAPI, ProviderServiceListAPI


api.add_resource(CategoryListAPI, '/categories')
api.add_resource(CategoryAPI, '/categories/<int:cat_id>')
api.add_resource(ProviderServiceListAPI, '/providers/<int:prov_id>/services')
api.add_resource(ProviderServiceAPI, '/providers/<int:prov_id>/services/<int:service_id>')
api.add_resource(CustomerBookingListAPI, '/customers/<int:cust_id>/bookings')
api.add_resource(CustomerBookingAPI, '/customers/<int:cust_id>/bookings/<int:booking_id>')