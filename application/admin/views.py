from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from application.decorators import role_required
from application.admin.forms import CategoryRegisterForm
from application.providers.enums import BookingStatusEnum, ServiceStatusEnum
from application.extensions import db
from . import admin
from .models import Admin, Category
from application.core.models import  Profile, User
from application.core.enums import UserRoleEnum
from application.providers.models import Provider, Service
from application.customers.models import Customer, Booking
from .enums import UserStatusEnum
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError



@admin.route('/')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def dashboard():
    return render_template('admin/dashboard.html')


# ---------------------------------------------------------------
# -----------------------Categories------------------------------
# ---------------------------------------------------------------

@admin.route('/categories')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_categories():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    form = CategoryRegisterForm()

    try:
        prov_with_active_services = (
            db.session.query(
                Provider, 
                db.func.count(
                    db.case((db.and_( Service.is_approved==True, Service.is_active==True, Service.is_blocked==False), Service.id))
                ).label('active_services')
            )
            .outerjoin(Service, Provider.services) \
            .filter(Provider.is_blocked==False, Provider.is_approved==True) \
            .group_by(Provider.id)
            .subquery()
        ) 

        categories = (
            db.session.query(
                Category, 
                db.func.count(prov_with_active_services.c.id),
                db.func.sum(prov_with_active_services.c.active_services)
            )
            .outerjoin(prov_with_active_services)
            .group_by(Category.id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/all_categories.html', categories=categories, form=form)


@admin.route('/categories/<int:category_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_category(category_id):
    category = Category.query.filter_by(id=category_id).first()

    data = db.session.query(Category, Provider, Service).join(Provider, Service.provider).join(Category, Provider.category).filter(Category.id == category_id).all()
    print(data)
    try:
        pass
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/single_category.html', category=category, data=data)


@admin.route('/categories/add', methods=['POST'])
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def add_new_category():
    form = CategoryRegisterForm()
    admin = Admin.query.first()

    if form.validate_on_submit():
        name = form.data.get('name')
        base_price = form.data.get('base_price')
        min_time_hr = form.data.get('min_time_hr')
        service_rate = form.data.get('service_rate')
        booking_rate = form.data.get('booking_rate')
        transaction_rate = form.data.get('transaction_rate')
        short_description = form.data.get('short_description')
        long_description = form.data.get('long_description')

        new_category = Category(
            name=name, base_price=base_price, min_time_hr=min_time_hr, \
            service_rate=service_rate, booking_rate=booking_rate, transaction_rate=transaction_rate, \
            short_description=short_description, long_description=long_description)

        admin.categories.append(new_category)
        try:
            db.session.add(new_category)
            db.session.commit() 
        except SQLAlchemyError as e:
            db.session.rollback()
            raise InternalServerError()
    return redirect(url_for('admin.get_all_categories'))



@admin.route('/categories/edit')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def edit_category():
    pass


# ---------------------------------------------------------------
# -----------------------Providers-------------------------------
# ---------------------------------------------------------------

@admin.route('/providers')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_providers():
    re = db.session.query(Provider, Category.id, Category.name, User.username, Provider.wallet, db.func.count(Service.id)).join(Provider, Category.id == Provider.category_id).join(User, User.id == Provider.user_id).join(Service, isouter=True).group_by(Provider.id).filter(Provider.is_approved.is_(True), Provider.is_blocked.is_(False)).order_by(Provider.created_at.desc()).all()

    print(re)

    # db.func.count(db.case(( db.and_(Service.is_blocked.is_(False), Service.is_active.is_(True)) , Service.id ))).label('active_service_count')
    # db.func.count(db.case([(Service.is_active == True, Service.id)], else_=None)).label('active_service_count')

    # providers = Provider.query.filter_by(is_approved=True).all()
    
    providers = db.session.query(Provider, db.func.count(db.case((db.and_(Service.is_approved.is_(True), Service.is_active.is_(True)), Service.id))).label('active_service_count'), db.func.count(Booking.id)).outerjoin(Service, Provider.services).outerjoin(Booking, Service.bookings).filter(Provider.is_approved.is_(True)).group_by(Provider.id).all()
    
    # providers = db.session.query(Provider,
    # db.func.count(db.case([(db.and_(Service.is_approved == True, Service.is_active == True), Service.id)])).label('active_service_count'),
    # db.func.count(Booking.id).label('total_bookings')).outerjoin(Service, Provider.services).outerjoin(Booking, Service.bookings).filter(Provider.is_approved.is_(True)).group_by(Provider.id).all()


    db.session.query(Service, db.func.count(Booking.id)).outerjoin(Booking, Service.bookings).filter(Service.is_approved.is_(True), Service.is_active.is_(True), Service.is_blocked.is_(False)).group_by(Service.id).all()



    return render_template('admin/all_providers.html', providers=providers, status_enum=UserStatusEnum)


@admin.route('/providers/<int:prov_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_provider(prov_id):
    provider = Provider.query.filter_by(id=prov_id).first()
    return render_template('admin/single_provider.html', provider=provider)


@admin.route('/approvals/providers')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_new_providers_joined():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)

    try:
        new_providers = (
            db.session.query(
                Provider, Category.name, Profile.location
            )
            .join(Category, Provider.category) \
            .join(Profile, Provider.user_id == Profile.user_id) \
            .filter(Provider.is_approved.is_(False), Provider.is_blocked.in_([False, True])) \
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/new_providers.html', new_providers=new_providers, status_enum=UserStatusEnum)


@admin.route('/approvals/providers/<int:prov_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def handle_provider(prov_id):
    status = request.args.get('status', type=str, default=UserStatusEnum.APPROVE.value)
    next = request.args.get('next')

    if status not in [status.value for status in UserStatusEnum]:
        raise BadRequest('provide valid status query parameter')

    provider = Provider.query.filter_by(id=prov_id).first()

    if provider:
        if status == UserStatusEnum.APPROVE.value:
            provider.is_approved = True
            provider.approved_at = datetime.today()
        elif status == UserStatusEnum.BLOCK.value:
            provider.is_blocked = True
        elif status == UserStatusEnum.UNBLOCK.value:
            provider.is_blocked = False
    else:
        raise NotFound('Not found provider')

    db.session.commit()
    if next:
        return redirect(next)
    return redirect(url_for('admin.get_all_providers'))


# ---------------------------------------------------------------
# -----------------------Customers--------------------------------
# ---------------------------------------------------------------

@admin.route('/customers')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_customers():
    customers = Customer.query.all()
    return render_template('admin/all_customers.html', customers=customers, status_enum=UserStatusEnum)


@admin.route('/customers/<int:cust_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_customer(cust_id):
    customer = Customer.query.filter_by(id=cust_id).first()
    return render_template('admin/single_customer.html', customer=customer)


@admin.route('/approvals/customers/<int:cust_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def handle_customer(cust_id):
    status = request.args.get('status', type=str, default=UserStatusEnum.APPROVE.value)

    if status not in [status.value for status in UserStatusEnum]:
        raise BadRequest('provide valid status query parameter')

    customer = Customer.query.filter_by(id=cust_id).first()

    if customer:
        if status == UserStatusEnum.BLOCK.value:
            customer.is_blocked = True
        elif status == UserStatusEnum.UNBLOCK.value:
            customer.is_blocked = False
    else:
        raise NotFound('Not found customer')
    db.session.commit()
    return redirect(url_for('admin.get_all_customers'))



# ---------------------------------------------------------------
# -----------------------Services--------------------------------
# ---------------------------------------------------------------

@admin.route('/services')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_services():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    try:
        services = (
            db.session.query(
                Service,
                db.func.count(
                    db.case((Booking.status == BookingStatusEnum.ACTIVE.value, Booking.id))
                ).label('active_bookings')
            )
            .outerjoin(Booking, Service.bookings)
            .group_by(Service.id)
            .filter(Service.is_approved==True)
            .all()
        )
        print(services)
        services = Service.query.filter_by(is_approved=True).all()
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/all_services.html', services=services, service_status_enum=ServiceStatusEnum)


@admin.route('/approvals/services')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_new_services_listed():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    try:
        services = Service.query.filter_by(is_approved=False).paginate(page=page, per_page=per_page)
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/new_services.html', services=services, service_status_enum=ServiceStatusEnum)


@admin.route('/approvals/services/<int:service_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def handle_service(service_id):
    status = request.args.get('status', type=str, default=ServiceStatusEnum.APPROVE.value)
    next = request.args.get('next')

    if status not in [status.value for status in ServiceStatusEnum]:
        raise BadRequest('provide valid status query parameter')
    
    service = Service.query.filter_by(id=service_id).first()

    if service:
        if status == ServiceStatusEnum.APPROVE.value:
            service.is_approved = True
            service.approved_at = datetime.today()
            flash(f'{service.title} is approved')
        elif status == ServiceStatusEnum.BLOCK.value:
            service.is_blocked = True
            flash(f'{service.title} is blocked')
        elif status == ServiceStatusEnum.UNBLOCK.value:
            service.is_blocked = False
            flash(f'{service.title} is unblocked')
    else:
        raise NotFound('Not found service')
    db.session.commit()
    if next:
        return redirect(next)
    return redirect(url_for('admin.get_all_services'))


@admin.route('/services/<int:service_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    return render_template('admin/single_service.html', service=service)


# ---------------------------------------------------------------
# -----------------------Bookings--------------------------------
# ---------------------------------------------------------------

@admin.route('/bookings')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_bookings():
    bookings = Booking.query.all()
    return render_template('admin/all_bookings.html', bookings=bookings)


@admin.route('/bookings/<int:booking_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_booking(booking_id):
    booking = Booking.query.filter_by(id=booking_id).first()
    return render_template('admin/single_booking.html', booking=booking)



















