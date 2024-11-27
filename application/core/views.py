from flask import current_app, render_template, request
from flask_login import current_user

from application.extensions import db
from application.core.models import Profile, User
from application.customers.forms import BookingForm
from application.admin.models import Category
from . import core
from application.providers.models import Service, Provider
from werkzeug.exceptions import NotFound, InternalServerError
from sqlalchemy.exc import SQLAlchemyError


@core.route('/')
def home():
    return render_template('home.html')


@core.route('/main/categories')
def get_all_categories():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)

    active_provs_with_active_services_subq = (
        db.session.query(
            Provider, 
            db.func.count(
                db.case(
                    (db.and_(Service.is_blocked.is_(False), Service.is_active.is_(True)), Service.id)
                )
            ).label('active_services')
        )
        .outerjoin(Service, Provider.services)
        .filter(Provider.is_blocked.is_(False), Provider.is_approved.is_(True))
        .group_by(Provider.id)
        .subquery() 
    )

    categories = (
        db.session.query(
            Category, 
            db.func.count(active_provs_with_active_services_subq.c.id), 
            db.func.sum(active_provs_with_active_services_subq.c.active_services)
        )
        .outerjoin(active_provs_with_active_services_subq)
        .group_by(Category.id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('core/all_categories.html', categories=categories)


@core.route('/main/categories/<int:cat_id>')
def get_single_category(cat_id):
    try:
        category = (
            db.session.query(
                Category
            )
            .filter(Category.id.is_(cat_id))
            .first()
        )

        if category is None:
            raise NotFound('No category found')
    except SQLAlchemyError as e:
        print(e)
        raise InternalServerError()
    return render_template('core/single_category.html', category=category)


@core.route('/main/services')
def get_all_listed_services():
    cat_id = request.args.get('cat_id', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)

    try:
        active_services_q = (
            db.session.query(
                Service, Provider, Profile
            )
            .outerjoin(Provider, Service.provider)
            .join(User, Provider.user)
            .join(Profile, User.profile)
            .filter(
                Provider.is_approved.is_(True),
                Provider.is_blocked.is_(False), 
                Service.is_approved.is_(True),
                Service.is_blocked.is_(False), 
                Service.is_active.is_(True)
            )
        )

        if cat_id:
            active_services_q = (
                active_services_q
                .join(Category, Provider.category)
                .filter(Category.id.is_(cat_id))
            )

        services = active_services_q.paginate(page=page, per_page=per_page, error_out=False)

    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('core/all_services.html', services=services)


@core.route('/main/services/<int:service_id>')
def get_listed_service(service_id):
    form = BookingForm()
    try:
        service, provider = (
            db.session.query(
                Service,
                Provider
            )
            .join(Provider, Service.provider)
            .filter(
                Service.id == service_id, Service.is_approved == True, Service.is_blocked == False, Service.is_active == True
            )
            .first()
        )
        if service is None:
            raise NotFound('Service not found')
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('core/single_service.html', service=service, provider=provider, form=form)


@core.route('/main/providers/<int:prov_id>')
def get_verified_provider(prov_id):
    try:
        provider, profile = (
            db.session.query(
                Provider,
                Profile,
            )
            .join(User, Provider.user)
            .join(Profile, User.profile)
            .filter(
                Provider.id==prov_id, Provider.is_approved==True, Provider.is_blocked==False
            )
            .first()
        )
        if provider is None:
            raise NotFound('Provider not found')
        
    except SQLAlchemyError as e:
        print(e)
        raise InternalServerError()
    return render_template('core/provider_profile.html', provider=provider, profile=profile)