
from collections import OrderedDict
from flask import abort, make_response
from flask_restful import Api, Resource, fields, marshal, marshal_with, reqparse

from application.admin.models import Admin, Category
from application.providers.models import Provider, Service
from . import bp
from application.extensions import db
from flask_login import login_required
from werkzeug.exceptions import HTTPException , Conflict
from sqlalchemy.exc import SQLAlchemyError

api = Api(bp)

booking_fields = {

}

service_fields = OrderedDict([
    ('id', fields.Integer),
    ('is_approved', fields.Boolean),
    ('is_active', fields.Boolean),
    ('is_blocked', fields.Boolean),
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
    ('username', fields.String),
    ('role', fields.String),
    ('profile', fields.Nested(profile_fields))
])

provider_fields = OrderedDict([
    ('id', fields.Integer),
    ('user_id', fields.Integer),
    ('experience', fields.Integer),
    ('wallet', fields.Integer),
    ('created_at', fields.DateTime),
    ('user', fields.Nested(user_fields)),
])

category_fields = OrderedDict([
    ('id', fields.Integer),
    ('name', fields.String),
    ('base_price', fields.Integer),
    ('providers', fields.List(fields.Nested(provider_fields)))
])

category_create_parser = reqparse.RequestParser()

category_create_parser.add_argument('name', type=str, required=True, trim=True)
category_create_parser.add_argument('base_price', type=int, required=True)
category_create_parser.add_argument('service_rate', type=int, required=True)
category_create_parser.add_argument('booking_rate', type=int, required=True)
category_create_parser.add_argument('transaction_rate', type=int, required=True)
category_create_parser.add_argument('short_description', type=str, nullable=True)
category_create_parser.add_argument('long_description', type=str, nullable=True)


service_status_parser = reqparse.RequestParser()
service_status_parser.add_argument('status', type=str, location='args', choices=['active', 'all'], default='all')

service_create_parser = reqparse.RequestParser()
service_create_parser.add_argument('title', type=str, trim=True, required=True)
service_create_parser.add_argument('price', type=int, required=True)
service_create_parser.add_argument('time_required_hr', type=int, required=True, help="time requied")
service_create_parser.add_argument('description', type=str, trim=True, nullable=False)



class CategoryListAPI(Resource):
    # decorators = [login_required]

    @marshal_with(category_fields)
    def get(self):
        try:
            categories = db.session.query(Category).all()
        except Exception as e:
            return {"message": "something went wrong"}, 500
        return categories, 200
    
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
        return make_response({"message": "new category created successfully", "category": marshal(new_category, category_fields)}, 201)


class CategoryAPI(Resource):

    @marshal_with(category_fields)
    def get(self, cat_id):
        try:
            category = Category.query.filter_by(id=cat_id).first()

            if category is None:
                return {"message": "category not found"}, 404
        except:
            return {'message': 'something went wrong'}, 500
        return category, 200


class ProviderServiceListAPI(Resource):

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

            prov_resp = marshal(provider, provider_fields)
            services_resp = marshal(services, service_fields)
            prov_resp.update({'services': services_resp})
        except:
            return {"message": "something went wrong"}, 500
        return make_response({
            "data": prov_resp
        }, 200)
    
    def post(self, prov_id):
        try:
            data = service_create_parser.parse_args(strict=True)

            provider = Provider.query.filter_by(id=prov_id).first()
            if provider is None:
                return {"message": "provider not found"}, 400
            
            if not provider.is_approved:
                return {"message": "provider is not approved"}, 400
            elif provider.is_blocked:
                return {"message": "provider is blocked"}, 403

            errors = []

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
                return make_response({
                    "message": errors
                }, 400)

            new_service = Service(**data)
            provider.services.append(new_service)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return {"message": str(e) if e else "something went wrong" }, 500
        return make_response({
            "message": "new service created successfully",
            "service": marshal(new_service, service_fields)
        }, 201)


api.add_resource(CategoryListAPI, '/categories')
api.add_resource(CategoryAPI, '/categories/<int:cat_id>')
api.add_resource(ProviderServiceListAPI, '/providers/<int:prov_id>/services')