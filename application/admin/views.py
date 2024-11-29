from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from application.customers.eums import CustomerPaymentStatusEnum
from application.decorators import role_required
from application.admin.forms import CategoryRegisterForm
from application.providers.enums import BookingStatusEnum, ServiceStatusEnum
from application.extensions import db
from . import admin
from .models import Admin, Category
from application.core.models import  Profile, User
from application.core.enums import UserRoleEnum
from application.providers.models import Provider, Service
from application.customers.models import Customer, Booking, CustomerPayment
from .enums import UserStatusEnum
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from collections import namedtuple




@admin.route('/')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def dashboard():
    try:
        prov_serv_res = (
            db.session.query(
                db.func.count(
                    db.distinct(Provider.id)
                ).label('active_providers'),
                db.func.count(
                    db.case(
                        (db.and_(Service.is_active==True, Service.is_approved==True, Service.is_blocked==False), Service.id)
                    )
                ).label('active_services'),
            )
            .join(Service, Provider.services)
            .filter(
                Provider.is_approved==True, Provider.is_blocked==False
            )
            .first()
        )    

        cust_book_payment_res = (
            db.session.query(
                db.func.count(
                    db.distinct(
                        db.case(
                            (Customer.is_blocked==False, Customer.id)
                        )
                    )
                ).label('active_customers'),
                db.func.count(
                    db.distinct(
                        db.case(
                            (Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value]), Booking.id)
                        )
                    )
                ).label('active_bookings'),
                db.func.count(
                    db.distinct(
                        db.case(
                            (Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value]), Booking.id)
                        )
                    )
                ).label('total_bookings'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (db.and_(CustomerPayment.status==CustomerPaymentStatusEnum.PAID.value, Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value])), CustomerPayment.final_provider_amount)
                        )
                    ), 0
                ).label('total_pending_payments'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (db.and_(CustomerPayment.status==CustomerPaymentStatusEnum.PAID.value, Booking.status.in_([BookingStatusEnum.CLOSE.value])), CustomerPayment.final_provider_amount)
                        )
                    ), 0
                ).label('total_payments_handout'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (CustomerPayment.status==CustomerPaymentStatusEnum.PAID.value, CustomerPayment.final_admin_amount)
                        )
                    ), 0
                ).label('total_revenue_generated'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (CustomerPayment.status==CustomerPaymentStatusEnum.PAID.value, CustomerPayment.total_amount)
                        )
                    ), 0
                ).label('total_payments_made'),
            )
            .outerjoin(Booking, Customer.bookings)
            .outerjoin(CustomerPayment, Booking.payment)
            .first()
        )

        AdminDashboardMetrics = namedtuple('AdminDashboardMetrics', ['active_providers', 'active_services', 'active_customers', 'active_bookings', 'total_bookings', 'total_pending_payments', 'total_payments_handout', 'total_revenue_generated', 'total_payments_made'])
        
        admin_dashboard_metrics = AdminDashboardMetrics(*prov_serv_res, *cust_book_payment_res) 

    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/dashboard.html', admin_dashboard_metrics=admin_dashboard_metrics)


@admin.route('/categories')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_categories():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    form = CategoryRegisterForm()

    try:
        categories = (
            db.session.query(
                Category,
                db.func.coalesce(
                    db.func.count(
                        db.distinct(
                            db.case((db.and_(Provider.is_approved==True, Provider.is_blocked==False), Provider.id))
                        )
                    ), 0
                ).label('active_providers'),
                db.func.coalesce(
                    db.func.count(
                        db.distinct(
                            db.case((db.and_(Service.is_approved==True, Service.is_blocked==False, Service.is_active, Provider.is_approved==True, Provider.is_blocked==False), Service.id))
                        )
                    ), 0
                ).label('active_services'),
                db.func.coalesce(
                    db.func.count(
                        db.distinct(
                            db.case((Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value]), Booking.id))
                        )
                    ), 0
                ).label('total_bookings'),
            )
            .outerjoin(Provider, Category.providers)
            .outerjoin(Service, Provider.services)
            .outerjoin(Booking, Service.bookings)
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
    try:
        category, *category_stats = (
            db.session.query(
                Category,
                db.func.coalesce(
                    db.func.count(
                        db.distinct(
                            db.case((db.and_(Provider.is_approved==True, Provider.is_blocked==False), Provider.id))
                        )
                    ), 0
                ).label('active_providers'),
                db.func.coalesce(
                    db.func.count(
                        db.distinct(
                            db.case((db.and_(Service.is_approved==True, Service.is_blocked==False, Service.is_active, Provider.is_approved==True, Provider.is_blocked==False), Service.id))
                        )
                    ), 0
                ).label('active_services'),
                db.func.coalesce(
                    db.func.count(
                        db.distinct(
                            db.case((Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value]), Booking.id))
                        )
                    ), 0
                ).label('total_bookings'),  
                db.func.coalesce(
                    db.func.sum(
                        db.case((CustomerPayment.status.is_(CustomerPaymentStatusEnum.PAID.value), CustomerPayment.final_admin_amount))
                    ), 0
                ).label('total_revenue'),  
            )
            .outerjoin(Provider, Category.providers)
            .outerjoin(Service, Provider.services)
            .outerjoin(Booking, Service.bookings)
            .outerjoin(CustomerPayment, Booking.payment)
            .group_by(Category.id)
            .filter(Category.id == category_id)
            .first()
        )

        services = (
            db.session.query(
                Service
            )
            .join(Provider, Service.provider)
            .join(Category, Provider.category)
            .filter(
                Category.id == category_id,
                Provider.is_approved==True, Provider.is_blocked==False,
                Service.is_active==True, Service.is_approved==True, Service.is_blocked==False
            )
            .all()
        )

        providers = (
            db.session.query(
                Provider
            )
            .join(Category, Provider.category)
            .filter(
                Category.id == category_id,
                Provider.is_approved==True, Provider.is_blocked==False,
            )
            .all()
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/single_category.html', category=category, category_stats=category_stats, services=services, providers=providers)


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

        try:
            new_category = Category(
                name=name, base_price=base_price, min_time_hr=min_time_hr, \
                service_rate=service_rate, booking_rate=booking_rate, transaction_rate=transaction_rate, \
                short_description=short_description, long_description=long_description)

            admin.categories.append(new_category)
            db.session.add(new_category)
            db.session.commit() 
        except SQLAlchemyError as e:
            db.session.rollback()
            raise InternalServerError()
    return redirect(url_for('admin.get_all_categories'))


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
                Provider
            )
            .outerjoin(Provider, Service.provider)
            .filter(Service.is_approved==True)
            .order_by(Service.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
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
        services = (
            Service.query
            .filter_by(is_approved=False)
            .order_by(Service.created_at.desc())
            .paginate(page=page, per_page=per_page)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/new_services.html', services=services, service_status_enum=ServiceStatusEnum)


@admin.route('/approvals/services/<int:service_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def handle_service(service_id):
    status = request.args.get('status', type=str, default=ServiceStatusEnum.APPROVE.value)
    next = request.args.get('next')

    try:
        if status not in [status.value for status in ServiceStatusEnum]:
            raise BadRequest('provide valid status query parameter')
        
        service = Service.query.filter_by(id=service_id).first()

        if service:
            if status == ServiceStatusEnum.APPROVE.value:
                service.is_approved = True
                service.is_active = True
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
    except SQLAlchemyError as e:
        raise InternalServerError()
    if next:
        return redirect(next)
    return redirect(url_for('admin.get_all_services'))


@admin.route('/services/<int:service_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_service(service_id):
    try:
        service, provider = (
            db.session.query(
                Service,
                Provider
            )
            .join(Provider)
            .filter(Service.id==service_id)
            .first()
        )

        bookings = (
            db.session.query(
                Booking,
                Customer
            )
            .join(Service, Booking.service)
            .join(Customer, Booking.customer)
            .filter(
                Booking.status.isnot(BookingStatusEnum.PENDING.value),
                Service.id==service.id
            )
            .order_by(Booking.id.desc())
            .all()
        )

        if service is None:
            raise NotFound('No such service found')
    except SQLAlchemyError as e:
        raise InternalServerError()

    return render_template('admin/single_service.html', service=service, provider=provider, bookings=bookings, booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum)


@admin.route('/providers')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_providers():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)

    try:
        providers = (
            db.session.query(
                Provider
            )
            .filter(Provider.is_approved.is_(True)) 
            .order_by(Provider.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/all_providers.html', providers=providers, status_enum=UserStatusEnum)


@admin.route('/providers/<int:prov_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_provider(prov_id):
    try:
        provider = (
            db.session.query(
                Provider
            )
            .options(
                db.joinedload(Provider.user).joinedload(User.profile)
            )
            .filter(Provider.id == prov_id)
            .first()
        )

        services = provider.services.all()

        bookings = (
            db.session.query(
                Booking
            )
            .join(Service, Booking.service)
            .join(Provider, Service.provider)
            .filter(
                Provider.id == prov_id,
                Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value])
            )
            .all()
        )
    except SQLAlchemyError as e:
        raise InternalServerError()  
    return render_template('admin/single_provider.html', provider=provider, services=services, bookings=bookings, booking_status_enum=BookingStatusEnum)


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
            .filter(Provider.is_approved.is_(False), Provider.is_blocked.in_([False, True])) 
            .order_by(Provider.created_at.desc())
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
        raise BadRequest()

    try:
        provider = Provider.query.filter_by(id=prov_id).first()

        if provider:
            if status == UserStatusEnum.APPROVE.value:
                provider.is_approved = True
                provider.approved_at = datetime.today()
                flash('provider approved', 'success')
            elif status == UserStatusEnum.BLOCK.value:
                provider.is_blocked = True
                flash('provider blocked', 'success')
            elif status == UserStatusEnum.UNBLOCK.value:
                provider.is_blocked = False
                flash('provider unblocked', 'success')
        else:
            raise NotFound('Not found provider')

        db.session.commit()
    except SQLAlchemyError as e:
        raise InternalServerError()
    if next:
        return redirect(next)
    return redirect(url_for('admin.get_all_providers'))


@admin.route('/customers')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_customers():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    try:
        customers = (
            db.session.query(
                Customer,
                db.func.count(
                    db.case(
                        (Booking.status.is_(BookingStatusEnum.ACTIVE.value), Booking.id)
                    )
                ).label('total_active_bookings'),
                db.func.count(
                    db.case(
                        (Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value]), Booking.id)
                    )
                ).label('total_bookings'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (CustomerPayment.status.is_(CustomerPaymentStatusEnum.PAID.value), CustomerPayment.total_amount)
                        )
                    ), 0
                )
                .label('lifetime_spent'),
            )
            .outerjoin(Booking, Customer.bookings)
            .outerjoin(CustomerPayment, Booking.payment)
            .group_by(Customer.id)
            .order_by(Customer.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/all_customers.html', customers=customers, status_enum=UserStatusEnum)


@admin.route('/customers/<int:cust_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_customer(cust_id):
    try:
        customer, *cust_stats = (
            db.session.query(
                Customer,
                db.func.count(
                    db.case((
                        db.and_(Booking.status.in_([BookingStatusEnum.ACTIVE.value])), Booking.id
                    ))
                ).label('active_bookings'),
                db.func.count(
                    db.case((
                        db.and_(Booking.status.in_([BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value])), Booking.id
                    ))
                ).label('completed_bookings'),
                db.func.count(
                    db.case((
                        db.and_(Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value])), Booking.id
                    ))
                ).label('total_bookings'),
                db.func.coalesce(
                    db.func.sum(
                        db.case((
                            db.and_(CustomerPayment.status.in_([CustomerPaymentStatusEnum.PAID.value])), CustomerPayment.total_amount
                        ))
                ), 0)
                .label('total_spent'),
            )
            .outerjoin(Booking, Customer.bookings)
            .outerjoin(CustomerPayment, Booking.payment)
            .filter(Customer.id == cust_id)
            .first()
        )
        bookings = (
            db.session.query(
                Booking,
                Service,
                CustomerPayment
            )
            .join(Service, Booking.service)
            .join(CustomerPayment, Booking.payment)
            .filter(Booking.customer_id == cust_id)
            .order_by(Booking.created_at.desc())
            .all()
        )

        reviews = []
        for booking, *other in bookings:
            if booking.review:
                reviews.append(booking.review)

    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/single_customer.html', customer=customer, cust_stats=cust_stats, bookings=bookings, reviews=reviews, booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum)


@admin.route('/approvals/customers/<int:cust_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def handle_customer(cust_id):
    status = request.args.get('status', type=str, default=UserStatusEnum.APPROVE.value)

    if status not in [status.value for status in UserStatusEnum]:
        raise BadRequest()

    customer = Customer.query.filter_by(id=cust_id).first()

    try:
        if customer:
            if status == UserStatusEnum.BLOCK.value:
                customer.is_blocked = True
                flash('customer blocked', 'success')
            elif status == UserStatusEnum.UNBLOCK.value:
                customer.is_blocked = False
                flash('customer unblocked', 'success')
        else:
            raise NotFound('Not found customer')
        db.session.commit()
    except SQLAlchemyError as e:
        raise InternalServerError()
    return redirect(url_for('admin.get_all_customers'))


@admin.route('/bookings')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_bookings():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    try:
        bookings = (
            db.session.query(
                Booking,
                Service,
                Customer
            )
            .join(Service, Booking.service)
            .join(Customer, Booking.customer)
            .group_by(Booking.id)
            .order_by(Booking.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('admin/all_bookings.html', bookings=bookings, booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum)


@admin.route('/bookings/<int:booking_id>')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_booking(booking_id):
    try:
        booking = (
            db.session.query(
                Booking
            )
            .options(
                db.joinedload(Booking.service).joinedload(Service.provider).joinedload(Provider.user).joinedload(User.profile)
            )
            .options(
                db.joinedload(Booking.customer).joinedload(Customer.user).joinedload(User.profile)
            )
            .options(db.joinedload(Booking.payment))
            .options(db.joinedload(Booking.review))
            .filter(Booking.id == booking_id)
            .first()
        )
    except SQLAlchemyError as e:
        raise InternalServerError() 
    return render_template('admin/single_booking.html', booking=booking, payment_status_enum=CustomerPaymentStatusEnum)


@admin.route('/payments')
@login_required
@role_required(UserRoleEnum.ADMIN.value)
def get_all_payments():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    try:
        payments = (
            db.session.query(
                CustomerPayment
            )
            .filter(CustomerPayment.status.is_(CustomerPaymentStatusEnum.PAID.value))
            .order_by(CustomerPayment.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError() 
    return render_template('admin/all_payments.html', payments=payments)



















