from datetime import datetime
from flask import make_response
from flask_restful import Resource, marshal

from application.admin.models import Admin, Category
from application.customers.models import Booking, Customer
from application.providers.models import Provider, Service
from application.extensions import db
from flask_login import login_required
from .fields import category_fields, service_fields, booking_fields
from .parsers import booking_create_parser, booking_status_parser, category_create_parser, service_create_parser, service_status_parser


class CategoryListAPI(Resource):
    decorators = [login_required]

    def get(self):
        try:
            categories = db.session.query(Category).all()
        except Exception as e:
            return {"message": "something went wrong"}, 500
        return make_response({
            "data": {
                "no_of_categories": len(categories),
                "categories": marshal(categories, category_fields)
            }
        })
    
    def post(self):
        data = category_create_parser.parse_args(strict=True)
        
        try:
            cat_name_exist =  Category.query.filter(Category.name.like(f'%{data['name']}%')).first()

            if cat_name_exist:
                return {"message": "category name already exists"}, 409

            admin = Admin.query.first()
            new_category = Category(**data)
            admin.categories.append(new_category)
            db.session.commit()
        except:
            db.session.rollback()
            return {'message': 'something went wrong'}, 500
        return make_response({
            "message": "new category created successfully", 
            "data": {"category": marshal(new_category, category_fields)}
        }, 201)

class CategoryAPI(Resource):
    decorators = [login_required]

    def get(self, cat_id):
        try:
            category = Category.query.filter_by(id=cat_id).first()

            if category is None:
                return {"message": "category not found"}, 404
        except:
            return {'message': 'something went wrong'}, 500
        return make_response({
            "data": {"category": marshal(category, category_fields)}
        }, 200)


class ProviderServiceListAPI(Resource):
    decorators = [login_required]

    def get(self, prov_id):
        args = service_status_parser.parse_args()
        try:
            provider = Provider.query.filter_by(id=prov_id).first()

            if provider is None:
                return {"message": "provider not found"}, 400
            
            if not provider.is_approved:
                return {"message": "provider is not approved"}, 400
            elif provider.is_blocked:
                return {"message": "provider is blocked"}, 403
            
            services_q = provider.services

            if args.get('status') == 'active':
                services_q = services_q.filter_by(
                    is_approved=True, is_blocked=False, is_active=True
                )

            services = services_q.all()
        except Exception as e:
            return {"message": "something went wrong"}, 500
        return make_response({
            "data": {
                "provider_id": provider.id, 
                "services": marshal(services, service_fields)
            }
        }, 200)
    
    def post(self, prov_id):
        try:
            data = service_create_parser.parse_args(strict=True)
            errors = []

            provider = Provider.query.filter_by(id=prov_id).first()
            if provider is None:
                return {"message": "provider not found"}, 404
            
            if not provider.is_approved:
                return {"message": "provider is not approved"}, 400
            elif provider.is_blocked:
                return {"message": "provider is blocked"}, 403


            if provider.category.base_price > data.get('price'):
                errors.append({
                    "field": "price",
                    "error": "service price should be above base price of category"
                })
            
            if provider.services.filter(Service.title.like(f'{data.get('title')}')).count() > 0:
                errors.append({
                    "field": "title",
                    "error": "title for service already exist"
                })

            if len(errors) > 0:
                return make_response({"message": errors}, 400)

            new_service = Service(**data)
            provider.services.append(new_service)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return {"message": str(e) if e else "something went wrong" }, 500
        return make_response({
            "message": "new service created successfully",
            "data": {"service": marshal(new_service, service_fields)}
        }, 201)

class ProviderServiceAPI(Resource):
    decorators = [login_required]

    def get(self, prov_id, service_id):
        try:
            provider = Provider.query.filter_by(id=prov_id).first()

            if provider is None:
                return {"message": "provider not found"}, 404
            
            if not provider.is_approved:
                return {"message": "provider is not approved"}, 403
            elif provider.is_blocked:
                return {"message": "provider is blocked"}, 403
            
            service = provider.services.filter(Service.id==service_id).first()

            if service is None:
                return {"message": "service not found"}, 404
        except:
            return {"message": "something went wrong"}, 500
        return make_response({
            "data": {"service": marshal(service, service_fields)}
        }, 200)




class CustomerBookingListAPI(Resource):
    decorators = [login_required]

    def get(self, cust_id):
        try:
            args = booking_status_parser.parse_args()
            customer = Customer.query.filter_by(id=cust_id).first()
            print(customer.id)
            if customer is None:
                return {"message": "customer not found"}, 404
            
            if customer.is_blocked:
                return {"message": "customer is blocked"}, 403
            
            bookings_q = customer.bookings

            if args.get('status'):
                bookings_q = bookings_q.filter(Booking.status==args.get('status'))
            
            bookings = bookings_q.all()

            bookings_resp = marshal(bookings, booking_fields)
        except Exception as e:
            print(e)
            return {"message": "something went wrong"}, 500
        return make_response({
            "data": {
                "customer_id": customer.id,
                "bookings": bookings_resp
            }
        }, 200)


    def post(self, cust_id):
        try:
            data = booking_create_parser.parse_args(strict=True)
            errors = []
            
            customer = Customer.query.filter_by(id=cust_id).first()

            if customer is None:
                return {"message": "customer not found"}, 404
            
            if customer.is_blocked:
                return {"message": "customer is blocked"}, 403
            
            service = Service.query.join(Provider).filter(
                Provider.is_blocked==False, Provider.is_approved==True,
                Service.is_approved==True, Service.is_active==True, Service.is_active==False,
                Service.id==data.get('service_id')
            )

            if service is None:
                return {"message": "service is not available or not found"}, 404
            
            if data.get('book_date').date() < datetime.now().date():
                errors.append({
                    "field": "book_date",
                    "error": "book date should be in the future or today"
                })

            if data.get('fullfillment_date').date() < datetime.now().date() or data.get('fullfillment_date').date() < data.get('book_date').date():
                errors.append({
                    "field": "fullfillment_date",
                    "error": "fullfillment date should be in the future or today"
                })
            
            if len(errors) > 0:
                return make_response({"message": errors}, 400)
            
            new_booking = Booking(customer_id=cust_id, **data)
            customer.bookings.append(new_booking)
            db.session.commit()

            bookin_resp = marshal(new_booking, booking_fields)
        except:
            db.session.rollback()
            return {"something went wrong"}, 500
        return make_response({
            "message": "new booking created successfully",
            "data": {"booking": bookin_resp}
        }, 201)

class CustomerBookingAPI(Resource):
    decorators = [login_required]

    def get(self, cust_id, booking_id):
        try:
            customer = Customer.query.filter_by(id=cust_id).first()

            if customer is None:
                return {"message": "customer not found"}, 404
            
            if customer.is_blocked:
                return {"message": "customer is blocked"}, 403
            
            booking = customer.bookings.filter_by(id=booking_id).first()

            if booking is None:
                return {"message": "booking not found"}, 404
        except:
            return {"message": "something went wrong"}, 500
        return make_response({
            "data": {"booking": marshal(booking, booking_fields)}
        }, 200)


