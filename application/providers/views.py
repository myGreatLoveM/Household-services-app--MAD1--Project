
from datetime import datetime
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from application.admin.models import Category
from application.core.models import Profile, User
from application.customers.eums import CustomerPaymentStatusEnum
from application.customers.models import Booking, Customer, CustomerPayment, Review
from application.extensions import db
from application.core.enums import UserRoleEnum
from application.decorators import role_required
from application.providers.enums import BookingStatusEnum, ServiceStatusEnum
from application.providers.forms import ServiceListingForm
from application.providers.models import Provider, Service
from . import provider
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError




@provider.route('/dashboard')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def dashboard(prov_id):
    try:
        prov_stats = (
            db.session.query(
                Provider.id.label('provider_id'),
                db.func.count(
                    db.distinct(
                        db.case(
                            (Service.is_active.is_(True), Service.id)
                        )
                    )
                ).label('total_active_services'),
                db.func.count(
                    db.case(
                        (db.and_(Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value])), Booking.id)
                    )
                ).label('total_bookings'),
                db.func.count(
                    db.case(
                        (db.and_(Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value])), Booking.id)
                    )
                ).label('active_bookings'),
                db.func.count(
                    db.case(
                        (db.and_(Booking.status.in_([BookingStatusEnum.CLOSE.value])), Booking.id)
                    )
                ).label('closed_bookings'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (Booking.status.in_([BookingStatusEnum.CLOSE.value]), CustomerPayment.amount)
                        )
                ), 0).label('total_lifetime_earning'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (Booking.status.in_([BookingStatusEnum.CLOSE.value]), CustomerPayment.service_fee)
                        )
                ), 0).label('total_lifetime_earning_service_feee'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value]), CustomerPayment.amount)
                        )
                ), 0).label('total_pending_earning'),
                db.func.coalesce(
                    db.func.sum(
                        db.case(
                            (Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value]), CustomerPayment.service_fee)
                        )
                ), 0).label('total_pending_earning_service_fee'),
                db.func.coalesce(
                    db.func.round(
                        db.func.avg(
                            db.case(
                                (Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value]), CustomerPayment.amount)
                            )
                        ), 2
                    ), 0
                ).label('avg_booking_amount'),
                db.func.coalesce(db.func.avg(Review.rating), 0).label('avg_rating'),
                db.func.count(Review.id).label('total_reviews')
            )
            .outerjoin(Service, Provider.services) 
            .outerjoin(Booking, Service.bookings) 
            .outerjoin(CustomerPayment, Booking.payment) 
            .outerjoin(Review, Booking.review) 
            .filter(
                Provider.id == prov_id, Provider.is_approved == True, Provider.is_blocked == False,
                Service.is_approved == True, Service.is_blocked == False,
            ) 
            .group_by(Provider.id) 
            .first()
        )

        print(prov_stats)

        active_bookings = (
            db.session.query(
                Booking,
                Service,
                Customer
            )
            .join(Service, Booking.service)
            .join(Customer, Booking.customer)
            .join(Provider, Service.provider)
            .filter(Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value]), Provider.id==prov_id)
            .all()
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('provider/dashboard.html', prov_id=prov_id, prov_stats=prov_stats, active_bookings=active_bookings, booking_status_enum=BookingStatusEnum)


@provider.route('/services')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_all_services(prov_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    form = ServiceListingForm()
    
    try:
        services = (
            db.session.query(
                Service,
            )
            .filter(Service.provider_id == prov_id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'provider/all_services.html', services=services, prov_id=prov_id, form=form, service_status_enum=ServiceStatusEnum
    )


@provider.route('/services/<int:service_id>')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_service(prov_id, service_id):
    try:
        service = (
            db.session.query(
                Service
            )
            .filter(Service.id==service_id, Service.provider_id==prov_id)
            .first()
        )

        # bookings = service.bookings.filter(Booking.status.isnot(BookingStatusEnum.PENDING.value)).all()
        
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
            # .paginate(page=page, per_page=per_page, error_out=False)
        )

        print(bookings)

        if service is None:
            raise NotFound('No such service found')
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('provider/single_service.html', prov_id=prov_id, service=service, bookings=bookings, booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum)


@provider.route('/services', methods=['POST'])
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def list_new_service(prov_id):
    form = ServiceListingForm()
    
    if form.validate_on_submit():
        title = form.title.data
        price = form.price.data
        time_required_hr = form.time_required_hr.data
        availability = form.availability.data
        description = form.description.data

        if Service.query.filter(Service.title.like(title)).count() == 0:
            new_service = Service(title=title, price=price, description=description, availability=availability, time_required_hr=time_required_hr, provider_id=prov_id)

            try:
                db.session.add(new_service)
                db.session.commit()
                flash('new service listed successfully', 'success')
            except:
                db.session.rollback()
                raise InternalServerError()
        else:
            flash('service title already exists', 'error')
    return redirect(url_for('provider.get_all_services', prov_id=prov_id))


@provider.route('/services/<int:service_id>/handle')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def handle_service(prov_id, service_id):
    status = request.args.get('status', None)
    next = request.args.get('next', None)

    if status not in [ServiceStatusEnum.CONTINUE.value, ServiceStatusEnum.DISCONTINUE.value]:
        raise BadRequest()

    try:
        service = (
            db.session.query(
                Service
            )
            .filter(Service.id==service_id, Service.provider_id==prov_id, Service.is_approved==True, Service.is_blocked==False)
            .first()
        )

        if service is None:
            raise NotFound('Service not found')
        
        if status == ServiceStatusEnum.DISCONTINUE.value:
            if service.is_active:
                service.is_active = False
                flash('service discontinued', 'success')
        elif status == ServiceStatusEnum.CONTINUE.value:
            if not service.is_active:
                service.is_active = True
                flash('service continued', 'success')
        db.session.commit()
    except SQLAlchemyError as e:
        raise InternalServerError()
    if next:
        return redirect(next)
    return redirect(url_for('provider.get_all_services', prov_id=prov_id))



@provider.route('/bookings')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_all_bookings(prov_id):
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
            .join(Provider, Service.provider)
            .filter(Booking.status.isnot(BookingStatusEnum.PENDING.value), Provider.id==prov_id)
            .order_by(Booking.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'provider/all_bookings.html', prov_id=prov_id, bookings=bookings, 
        booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum
    )


@provider.route('/bookings/<int:booking_id>')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_single_booking(prov_id, booking_id):
    try:
        booking, service = (
            db.session.query(
                Booking,
                Service
            )
            .join(Service, Booking.service)
            .join(Provider, Service.provider)
            .filter(Booking.id== booking_id, Provider.id==prov_id)
            .first()
        )

        customer, profile = (
            db.session.query(
                Customer,
                Profile
            )
            .join(Booking, Customer.bookings)
            .join(User, Customer.user)
            .join(Profile, User.profile)    
            .filter(Booking.id== booking.id)
            .first()
        )

        if booking is None:
            raise NotFound('No such booking found for provider')
        
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'provider/single_booking.html', prov_id=prov_id, booking=booking,
        customer=customer,
        profile=profile,
        service=service,
        booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum
    )


@provider.route('bookings/new')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_all_new_bookings(prov_id):
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
            .join(Provider, Service.provider)
            .filter(Booking.status.is_(BookingStatusEnum.PENDING.value), Provider.id==prov_id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'provider/new_bookings.html', prov_id=prov_id, bookings=bookings, booking_status_enum=BookingStatusEnum
    )


@provider.route('/bookings/<int:booking_id>/handle')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def handle_booking(prov_id, booking_id):
    booking_status = request.args.get('status', None)
    next = request.args.get('next', None)

    if booking_status not in [BookingStatusEnum.REJECT.value, BookingStatusEnum.CONFIRM.value, BookingStatusEnum.CLOSE.value]:
        raise BadRequest()

    try:
        booking, provider, category = (
            db.session.query(
                Booking,
                Provider,
                Category
            )
            .join(Service, Booking.service)
            .join(Provider, Service.provider)
            .join(Category, Provider.category)
            .filter(Booking.id== booking_id, Provider.id==prov_id)
            .first()
        )

        if booking is None:
            raise NotFound('No such booking found for provider')

        if booking_status == BookingStatusEnum.REJECT.value:
            booking.status = BookingStatusEnum.REJECT.value
            flash('booking is rejected', category='success')
        elif booking_status == BookingStatusEnum.CONFIRM.value:
            booking.status = BookingStatusEnum.CONFIRM.value
            booking.confimation_date = datetime.today()

            service = booking.service
            amount = service.price * service.time_required_hr

            pending_payment = CustomerPayment(
                status = CustomerPaymentStatusEnum.PENDING.value,
                amount = amount,
                service_fee = round((category.service_rate * amount)/100),
                platform_fee = round((category.booking_rate * amount)/100),
                transaction_fee = round((category.transaction_rate * amount)/100)
            )

            booking.payment = pending_payment
            flash('booking confirmed', category='success')
        elif booking_status == BookingStatusEnum.CLOSE.value:
            if booking.status == BookingStatusEnum.COMPLETE.value:
                booking.status = BookingStatusEnum.CLOSE.value
                booking.closed_date = datetime.today()

                provider.wallet += booking.payment.calculate_provider_amount()
                flash('booking closed', category='success')
            else:
                flash('customer has not closed booking', category='error')
        db.session.commit()
    except SQLAlchemyError as e:
        raise InternalServerError()
    if next:
        return redirect(next)
    return redirect(url_for('provider.get_all_new_bookings', prov_id=prov_id))


@provider.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def profile(prov_id):
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

        if request.method == 'POST':
            provider.user.profile.full_name = request.form['full_name']
            provider.user.profile.email = request.form['email']
            provider.user.profile.contact = request.form['contact']
            provider.user.profile.location = request.form['location']
            provider.user.profile.bio = request.form['bio']

            db.session.commit()
            flash('details updated successfully!', category='success')
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while updating details.', category='error')
        raise InternalServerError() 
    return render_template('provider/profile.html', prov_id=prov_id, provider=provider)


@provider.route('/payments')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_all_payments(prov_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)

    try:
        payments = (
            db.session.query(
                CustomerPayment,
                Booking,
                Service,
                Customer
            )
            .join(Booking, CustomerPayment.booking)
            .join(Service, Booking.service)
            .join(Customer, Booking.customer)
            .filter(
                Service.provider_id.is_(prov_id),
                CustomerPayment.status.is_(CustomerPaymentStatusEnum.PAID.value)
            )
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    except SQLAlchemyError as e:
        raise InternalServerError() 
    return render_template('provider/all_payments.html', prov_id=prov_id, payments=payments, booking_status_enum=BookingStatusEnum)