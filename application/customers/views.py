from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from application.extensions import db
from . import customer
from .models  import Booking, Customer, CustomerPayment, Review
from .forms import BookingForm, CustomerPaymentForm, ReviewForm
from application.decorators import role_required
from application.core.models import Profile, User
from application.providers.models import Provider, Service
from application.customers.eums import CustomerPaymentStatusEnum
from application.providers.enums import BookingStatusEnum
from application.core.enums import UserRoleEnum


@customer.route('/dashboard')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def dashboard(cust_id):
    try:
        booking_stats = (
            db.session.query(
                db.func.count(
                    db.case((
                        db.and_(Booking.status.in_([BookingStatusEnum.ACTIVE.value, BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value])), Booking.id
                    ))
                ).label('total_bookings'),
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
                db.func.coalesce(
                    db.func.sum(
                        db.case((
                            db.and_(CustomerPayment.status.in_([CustomerPaymentStatusEnum.PAID.value])), CustomerPayment.total_amount
                        ))
                ), 0)
                .label('total_spent'),
            )
            .outerjoin(CustomerPayment, Booking.payment)
            .filter(Booking.customer_id == cust_id)
            .first()
        )

        prov_username_subq = (
            db.session.query(
                Provider.id, User.username
            )
            .join(User, Provider.user)
            .subquery()
        )

        active_bookings = (
            db.session.query(
                Booking, Service, prov_username_subq.c.username
            )
            .join(Service, Booking.service)
            .join(prov_username_subq, Service.provider_id==prov_username_subq.c.id)
            .join(Customer, Booking.customer)
            .filter(
                Booking.status.in_([BookingStatusEnum.ACTIVE.value]),
                Customer.id==cust_id
            )
            .all()
        )

        confirmed_bookings = (
            db.session.query(
                Booking, Service, prov_username_subq.c.username, CustomerPayment.id
            )
            .join(Service, Booking.service)
            .join(prov_username_subq, Service.provider_id==prov_username_subq.c.id)
            .join(Customer, Booking.customer)
            .outerjoin(CustomerPayment, Booking.payment)
            .filter(
                Booking.status.in_([BookingStatusEnum.CONFIRM.value]), 
                Customer.id==cust_id
            )
            .all()
        )

    except SQLAlchemyError as e:
        raise InternalServerError()
    
    return render_template(
        'customer/dashboard.html', cust_id=cust_id, booking_stats=booking_stats, active_bookings=active_bookings, confirmed_bookings=confirmed_bookings, booking_status_enum=BookingStatusEnum
    )


@customer.route('/<int:service_id>/book', methods=['POST'])
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def book_listed_service(cust_id, service_id):
    form = BookingForm()
    if form.validate_on_submit():
        book_date = form.data.get('book_date')
        fullfillment_date = form.data.get('fullfillment_date')
        remark = form.data.get('remark')

        new_booking = Booking(
                        book_date=book_date, fullfillment_date=fullfillment_date, 
                        remark=remark, service_id=service_id, customer_id=cust_id
                    )
        try:
            db.session.add(new_booking)
            db.session.commit()
            flash('service booked successfully', category='success')
        except SQLAlchemyError as e:
            raise InternalServerError()
    return redirect(url_for('core.get_listed_service', service_id=service_id))


@customer.route('/bookings')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_bookings(cust_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)

    try:
        prov_username_subq = (
            db.session.query(
                Provider.id, User.username
            )
            .join(User, Provider.user)
            .subquery()
        )

        bookings = (
            db.session.query(
                Booking, Service, prov_username_subq.c.username
            )
            .join(Service, Booking.service)
            .join(prov_username_subq, Service.provider_id==prov_username_subq.c.id)
            .join(Customer, Booking.customer)
            .filter(
                Booking.status.notin_([BookingStatusEnum.PENDING.value, BookingStatusEnum.CONFIRM.value]), 
                Customer.id==cust_id
            )
            .order_by(Booking.id.desc())
            .paginate(per_page=per_page, page=page, error_out=False)
        )

    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'customer/all_bookings.html', cust_id=cust_id, bookings=bookings, 
        booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum
    )


@customer.route('/bookings/<int:booking_id>')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_single_booking(cust_id, booking_id):
    form = ReviewForm()

    try:
        booking = (
            db.session.query(
                Booking
            )
            .options(
                db.joinedload(
                    Booking.service
                )
                .joinedload(Service.provider)
                .joinedload(Provider.user)
                .joinedload(User.profile)
            )
            .options(db.joinedload(Booking.payment))
            .options(db.joinedload(Booking.review))
            .filter(Booking.id==booking_id, Booking.customer_id==cust_id)
            .first()
        )   

        if booking is None:
            raise NotFound('No such booking found for customer')
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'customer/single_booking.html', cust_id=cust_id, booking=booking, 
        booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum, form=form
    )


@customer.route('/bookings/<int:booking_id>/handle')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def handle_booking(cust_id, booking_id):
    next = request.args.get('next', None)
    booking_status = request.args.get('status', None)

    if booking_status not in BookingStatusEnum.COMPLETE.value:
        raise BadRequest('provide valid status query parameter')

    try:
        booking = (
            db.session.query(
                Booking
            )
            .filter(Booking.id==booking_id, Booking.customer_id==cust_id)
            .first()
        )

        if booking is None:
            raise NotFound('No such booking found for customer')

        if booking_status == BookingStatusEnum.COMPLETE.value:
            if booking.status == BookingStatusEnum.ACTIVE.value:
                booking.status = BookingStatusEnum.COMPLETE.value
                booking.completed_date = datetime.today()
                flash('booking completed', category='success')
            else:
                flash('booking is not active', category='error')
        db.session.commit()
    except SQLAlchemyError as e:
        raise InternalServerError()
    if next:
        return redirect(next)
    return redirect(url_for('customer.get_all_bookings', cust_id=cust_id))


@customer.route('/bookings/pending')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_pending_bookings(cust_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)

    try:
        prov_username_subq = (
            db.session.query(
                Provider.id, User.username
            )
            .join(User, Provider.user)
            .subquery()
        )

        bookings = (
            db.session.query(
                Booking, Service, prov_username_subq.c.username, CustomerPayment.id
            )
            .join(Service, Booking.service)
            .join(prov_username_subq, Service.provider_id==prov_username_subq.c.id)
            .join(Customer, Booking.customer)
            .outerjoin(CustomerPayment, Booking.payment)
            .filter(
                Booking.status.in_([BookingStatusEnum.PENDING.value, BookingStatusEnum.CONFIRM.value]), 
                Customer.id==cust_id
            )
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'customer/pending_bookings.html', cust_id=cust_id,
        bookings=bookings, booking_status_enum=BookingStatusEnum
    )



@customer.route('/payments')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_payments(cust_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)
    
    try:
        payments = (
            db.session.query(
                CustomerPayment,
                Booking,
                Service,
                Provider
            )
            .join(Booking, CustomerPayment.booking)
            .join(Service, Booking.service)
            .join(Provider, Service.provider)
            .filter(
                Customer.id==cust_id, 
                CustomerPayment.status.notin_([CustomerPaymentStatusEnum.PENDING.value])
            )
            .order_by(CustomerPayment.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('customer/all_payments.html', cust_id=cust_id, payments=payments)


@customer.route('/payments/pending')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_pending_payments(cust_id):
    form = CustomerPaymentForm()
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 6)

    try:
        pending_payments = (
            db.session.query(
                CustomerPayment, 
                Booking,
                Service,
                Provider
            )
            .join(Booking, CustomerPayment.booking)
            .join(Service, Booking.service)
            .join(Provider, Service.provider)
            .filter(
                CustomerPayment.status.is_(CustomerPaymentStatusEnum.PENDING.value),
                Booking.customer_id.is_(cust_id)
            )
            .order_by(CustomerPayment.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        ) 
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template(
        'customer/pending_payments.html', cust_id=cust_id,
        payments=pending_payments, form=form
    )


@customer.route('/payments/<int:payment_id>')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def go_to_payment_portal(cust_id, payment_id):
    next = request.args.get('next', None)
    form = CustomerPaymentForm()
    try:
        payment = (
            db.session.query(
                CustomerPayment
            )
            .join(Booking)
            .join(Customer)
            .filter(CustomerPayment.id==payment_id, Customer.id==cust_id)
            .first()
        )

        if payment is None:
            raise NotFound("No such payment found for customer")
    except SQLAlchemyError as e:
        raise InternalServerError()
    return render_template('customer/payment.html', cust_id=cust_id, payment=payment, form=form, next=next)


@customer.route('/payments/<int:payment_id>/handle', methods=['GET', 'POST'])
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def handle_payment(cust_id, payment_id):
    next = request.args.get('next', None)
    form = CustomerPaymentForm()
    if request.method == 'POST' and form.validate_on_submit():
        method = form.data.get('method')
        try:
            payment = (
                db.session.query(
                        CustomerPayment
                    )
                    .join(Booking, CustomerPayment.booking)
                    .join(Customer, Booking.customer)
                    .filter(
                        CustomerPayment.id==payment_id, Customer.id==cust_id
                    ).first()
            )
            
            payment.method = method
            payment.status = CustomerPaymentStatusEnum.PAID.value
            payment.booking.status = BookingStatusEnum.ACTIVE.value
            db.session.commit()
            flash('payment successfull', category='success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('payment error', category='error')
            raise InternalServerError()
        if next:
            return redirect(next)
        return redirect(url_for('customer.get_all_pending_payments', cust_id=cust_id))
    return render_template('customer/payment.html', cust_id=cust_id, form=form, payment_id=payment_id)



@customer.route('/bookings/<int:booking_id>/review', methods=['POST'])
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def review_completed_booking(cust_id, booking_id):
    next = request.args.get('next', None, type=str)
    form = ReviewForm()

    if form.validate_on_submit():
        rating = form.rating.data
        comment = form.comment.data

        try:
            booking = (
                db.session.query(
                    Booking
                )
                .join(Customer)
                .filter(Booking.id.is_(booking_id), Customer.id.is_(cust_id))
                .first()
            )

            if booking is None:
                raise NotFound('Booking not found')

            if booking.status in [BookingStatusEnum.COMPLETE.value, BookingStatusEnum.CLOSE.value]:
                new_review = Review(
                    rating=rating, comment=comment, booking_id=booking_id
                )
                db.session.add(new_review)
                db.session.commit()
                flash('Review added successfully', 'success')
            else:
                flash('Booking is not closed', 'success')
        except SQLAlchemyError as e:
                db.session.rollback()
                flash('Review not added', 'error')
                raise InternalServerError()
    if next:
        return redirect(next)
    return redirect(url_for('customer.get_single_booking', cust_id=cust_id, booking_id=booking_id))    


@customer.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def profile(cust_id):
    try:
        customer = (
            db.session.query(
                Customer
            )
            .options(
                db.joinedload(Customer.user).joinedload(User.profile)
            )
            .filter(Customer.id == cust_id)
            .first()
        )

        if request.method == 'POST':
            customer.user.profile.full_name = request.form['full_name']
            customer.user.profile.email = request.form['email']
            customer.user.profile.contact = request.form['contact']
            customer.user.profile.location = request.form['location']
            customer.user.profile.bio = request.form['bio']

            db.session.commit()
            flash('details updated successfully!', category='success')
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while updating details.', category='error')
        raise InternalServerError() 
    return render_template('customer/profile.html', cust_id=cust_id, customer=customer)