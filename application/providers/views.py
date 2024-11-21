from datetime import datetime
from flask import abort, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required

from application.admin.models import Category
from application.customers.eums import CustomerPaymentStatusEnum
from application.customers.models import Booking, CustomerPayment
from application.providers.enums import BookingStatusEnum, ServiceStatusEnum
from . import provider
from .models import Provider, Service
from .forms import ServiceListingForm
from application.core.enums import UserRoleEnum
from application.decorators import role_required
from application.extensions import db
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError


@provider.route('/dashboard')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def dashboard(prov_id):
    return render_template('provider/dashboard.html', prov_id=prov_id)


@provider.route('/services')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_all_services(prov_id):
    form = ServiceListingForm()
    services = Service.query.filter(Service.provider_id == prov_id).all()
    print(services)

    s = db.session.query(
        Service,
        db.func.count(
            db.case((Booking.status.in_([BookingStatusEnum.ACTIVE.value]), Booking.id))
        ),
        db.func.sum(
            db.case((CustomerPayment.status.in_([CustomerPaymentStatusEnum.PAID.value]), CustomerPayment.service_cost))
        )
    ).outerjoin(Booking, Service.bookings).outerjoin(CustomerPayment, Booking.payment).group_by(Service.id).filter(Service.provider_id == prov_id).all()

    print(s)

    return render_template(
        'provider/all_services.html', services=services, prov_id=prov_id, form=form, service_status_enum=ServiceStatusEnum
    )


@provider.route('/services/<int:service_id>')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_service(prov_id, service_id):
    service = Service.query.filter(Service.id==service_id, Service.provider_id==prov_id).first()
    if not service:
        raise NotFound('No such service found')
    return render_template('provider/single_service.html', prov_id=prov_id, service=service)


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
    print(next)

    if status not in [status.value for status in ServiceStatusEnum]:
        raise BadRequest('provide valid status query parameter')

    service = Service.query.filter(Service.id==service_id, Service.provider_id==prov_id, Service.is_approved==True, Service.is_blocked==False).first()

    if service is None:
        raise NotFound('Service not found')
    
    if status == ServiceStatusEnum.DISCONTINUE.value:
        if service.is_active:
            print('Service is discontinue')
            service.is_active = False
    elif status == ServiceStatusEnum.CONTINUE.value:
        if not service.is_active:
            print('Service is continue')
            service.is_active = True
    db.session.commit()
    return redirect(url_for('provider.get_all_services', prov_id=prov_id))


@provider.route('/services/<int:service_id>', methods=['POST'])
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def edit_service(prov_id, service_id):
    pass



# ---------------------------------------------------------------
# -----------------------Booking---------------------------------
# ---------------------------------------------------------------

@provider.route('/bookings')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_all_bookings(prov_id):
    bookings = (
        db.session.query(
            Booking
        )
        .join(Service, Booking.service)
        .join(Provider, Service.provider)
        .filter(Booking.status.isnot(BookingStatusEnum.PENDING.value), Provider.id==prov_id)
        .all()
    )
    
    return render_template(
        'provider/all_bookings.html', prov_id=prov_id, bookings=bookings, 
        booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum
    )


@provider.route('/bookings/<int:booking_id>')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_single_booking(prov_id, booking_id):
    booking = (
        db.session.query(
            Booking
        )
        .join(Service, Booking.service)
        .join(Provider, Service.provider)
        .filter(Booking.id== booking_id, Provider.id==prov_id)
        .first()
    )

    if booking is None:
        raise NotFound('No such booking found for provider')
    return render_template(
        'provider/single_booking.html', prov_id=prov_id, booking=booking,
        booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum
    )

@provider.route('bookings/new')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def get_all_new_bookings(prov_id):
    bookings = (
        db.session.query(
            Booking
        )
        .join(Service, Booking.service)
        .join(Provider, Service.provider)
        .filter(Booking.status==BookingStatusEnum.PENDING.value, Provider.id==prov_id)
        .all()
    )

    return render_template(
        'provider/new_bookings.html', prov_id=prov_id, bookings=bookings, booking_status_enum=BookingStatusEnum
    )


@provider.route('/bookings/<int:booking_id>/handle')
@login_required
@role_required(UserRoleEnum.PROVIDER.value)
def handle_booking(prov_id, booking_id):
    status = request.args.get('status', None)

    if status not in [BookingStatusEnum.REJECT.value, BookingStatusEnum.CONFIRM.value, BookingStatusEnum.CLOSE.value]:
        raise BadRequest('provide valid status query parameter')

    booking, category = (
        db.session.query(
            Booking,
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

    if status == BookingStatusEnum.REJECT.value:
        booking.status = BookingStatusEnum.REJECT.value
        flash('booking is rejected', category='success')
    elif status == BookingStatusEnum.CONFIRM.value:
        booking.status = BookingStatusEnum.CONFIRM.value
        booking.confimation_date = datetime.today()

        service = booking.service
        service_cost = service.price * service.time_required_hr

        pending_payment = CustomerPayment(
            status = CustomerPaymentStatusEnum.PENDING.value,
            service_cost = service_cost,
            platform_fee = round((category.service_rate * service_cost)/100),
            transaction_fee = round((category.transaction_rate * service_cost)/100)
        )

        booking.payment = pending_payment
        flash('booking is confirmed', category='success')
    elif status == BookingStatusEnum.CLOSE.value:
        if booking.status == BookingStatusEnum.COMPLETE.value:
            booking.status = BookingStatusEnum.CLOSE.value
            booking.closed_date = datetime.today()
            flash('booking is closed', category='success')
        else:
            flash('customer has not closed booking', category='error')
    db.session.commit()
    return redirect(url_for('provider.get_all_bookings', prov_id=prov_id))


