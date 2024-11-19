from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from application.core.models import User
from application.customers.eums import CustomerPaymentStatusEnum
from application.providers.enums import BookingStatusEnum
from application.providers.models import Provider, Service
from . import customer
from application.core.enums import UserRoleEnum
from application.decorators import role_required
from .forms import BookingForm, CustomerPaymentForm, ReviewForm
from .models  import Booking, Customer, CustomerPayment, Review
from application.extensions import db
from werkzeug.exceptions import NotFound, Forbidden, BadRequest


@customer.route('/dashboard')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def dashboard(cust_id):
    return render_template('customer/dashboard.html', cust_id=cust_id)


@customer.route('/<int:service_id>/book', methods=['POST'])
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def book_listed_service(cust_id, service_id):
    form = BookingForm()
    if form.validate_on_submit():
        book_date = form.data.get('book_date')
        fullfillment_date = form.data.get('fullfillment_date')
        remark = form.data.get('remark')
        new_booking = Booking(book_date=book_date, fullfillment_date=fullfillment_date, remark=remark, service_id=service_id, customer_id=cust_id)
        db.session.add(new_booking)
        db.session.commit()
    return redirect(url_for('core.get_all_listed_services'))


@customer.route('/bookings')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_bookings(cust_id):
    prov_username_subq = db.session.query(Provider.id, User.username).join(User, Provider.user).subquery()

    bookings = db.session.query(Booking, Service, prov_username_subq.c.username).join(Service, Booking.service).join(prov_username_subq, Service.provider_id==prov_username_subq.c.id).join(Customer, Booking.customer).filter(Booking.status.notin_([BookingStatusEnum.PENDING.value, BookingStatusEnum.CONFIRM.value]), Customer.id==cust_id).all()

    return render_template('customer/all_bookings.html', cust_id=cust_id, bookings=bookings, booking_status_enum=BookingStatusEnum, payment_status_enum =CustomerPaymentStatusEnum)


@customer.route('/bookings/<int:booking_id>')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_single_booking(cust_id, booking_id):
    form = ReviewForm()

    booking = db.session.query(Booking).join(Customer, Booking.customer).filter(Booking.id==booking_id, Booking.customer_id==Customer.id).first()

    if booking is None:
        raise NotFound('No such booking found for customer')
    return render_template('customer/single_booking.html', cust_id=cust_id, booking=booking, booking_status_enum=BookingStatusEnum, payment_status_enum=CustomerPaymentStatusEnum, form=form)


@customer.route('/bookings/<int:booking_id>/handle')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def handle_booking(cust_id, booking_id):
    booking_status = request.args.get('status', None)

    if booking_status not in [status.value for status in BookingStatusEnum]:
        raise BadRequest('provide valid status query parameter')

    booking = db.session.query(Booking).join(Customer, Booking.customer).filter(Booking.id==booking_id, Booking.customer_id==Customer.id).first()

    if booking is None:
        raise NotFound('No such booking found for customer')

    if booking_status == BookingStatusEnum.COMPLETE.value:
        if booking.status == BookingStatusEnum.ACTIVE.value:
            booking.status = BookingStatusEnum.COMPLETE.value
            booking.completed_date = datetime.today()
        else:
            pass
    db.session.commit()
    return redirect(url_for('customer.get_all_bookings', cust_id=cust_id))


@customer.route('/bookings/pending')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_pending_bookings(cust_id):
    prov_username_subq = db.session.query(Provider.id, User.username).join(User, Provider.user).subquery()

    bookings = db.session.query(Booking, Service, prov_username_subq.c.username, CustomerPayment.id).join(Service, Booking.service).join(prov_username_subq, Service.provider_id==prov_username_subq.c.id).join(Customer, Booking.customer).outerjoin(CustomerPayment, Booking.payment).filter(db.or_(Booking.status.in_([BookingStatusEnum.PENDING.value]), db.and_(Booking.status.in_([BookingStatusEnum.CONFIRM.value]), CustomerPayment.status.is_(CustomerPaymentStatusEnum.PENDING.value))), Customer.id==cust_id).all()
    return render_template('customer/pending_bookings.html', cust_id=cust_id, bookings=bookings, booking_status_enum=BookingStatusEnum)



@customer.route('/payments')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_payments(cust_id):
    payments = db.session.query(CustomerPayment).join(Booking, CustomerPayment.booking).join(Customer, Booking.customer).filter(Customer.id==cust_id, CustomerPayment.status.notin_([CustomerPaymentStatusEnum.PENDING.value])).all()
    return render_template('customer/all_payments.html', cust_id=cust_id, payments=payments)


@customer.route('/payments/pending')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def get_all_pending_payments(cust_id):
    form = CustomerPaymentForm()
    pending_payments = db.session.query(CustomerPayment).join(Booking).join(Customer).filter(CustomerPayment.status==CustomerPaymentStatusEnum.PENDING.value , Customer.id==cust_id).all() 
    return render_template('customer/pending_payments.html', cust_id=cust_id, payments=pending_payments, form=form)


@customer.route('/payments/<int:payment_id>/handle', methods=['GET', 'POST'])
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def handle_payment(cust_id, payment_id):
    form = CustomerPaymentForm()
    if request.method == 'POST' and form.validate_on_submit():
        method = form.data.get('method')
        payment = db.session.query(CustomerPayment).join(Booking, CustomerPayment.booking).join(Customer, Booking.customer).filter(
            CustomerPayment.id==payment_id, Customer.id==cust_id
        ).first()
        payment.method = method
        payment.status = CustomerPaymentStatusEnum.PAID.value
        payment.booking.status = BookingStatusEnum.ACTIVE.value
        db.session.commit()
        return redirect(url_for('customer.get_all_pending_payments', cust_id=cust_id))

    return render_template('customer/payment.html', cust_id=cust_id, form=form, payment_id=payment_id)


@customer.route('/payments/<int:payment_id>')
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def go_to_payment_portal(cust_id, payment_id):
    payment = db.session.query(CustomerPayment).join(Booking).join(Customer).filter(CustomerPayment.id==payment_id, Customer.id==cust_id).first()
    form = CustomerPaymentForm()

    if payment is None:
        raise NotFound("No such payment found for customer")
    return render_template('customer/payment.html', cust_id=cust_id, payment=payment, form=form)


@customer.route('/bookings/<int:booking_id>/review', methods=['POST'])
@login_required
@role_required(UserRoleEnum.CUSTOMER.value)
def review_completed_booking(cust_id, booking_id):
    next = request.args.get('next', None, type=str)
    form = ReviewForm()

    if form.validate_on_submit():
        rating = form.rating.data
        comment = form.comment.data

        booking = db.session.query(Booking).join(Customer).filter(Booking.id.is_(booking_id), Customer.id.is_(cust_id)).first()

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
    else:
        flash('Review not added', 'error')
    
    if next:
        return redirect(next)
    return redirect(url_for('customer.get_single_booking', cust_id=cust_id, booking_id=booking_id))    
