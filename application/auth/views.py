from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required, login_user, logout_user, fresh_login_required
from werkzeug.exceptions import InternalServerError, NotFound
from . import auth
from application.auth.forms import LoginForm, CustomerRegisterForm, ProviderRegisterForm
from application.extensions import db
from application.core.models import User, Profile
from application.admin.models import Category
from application.customers.models import Customer
from application.providers.models import Provider
from application.core.enums import UserRoleEnum


@auth.before_request
def before_request():
    if request.endpoint in ['auth.login', 'auth.register']:
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif current_user.is_provider:
                return redirect(url_for('provider.dashboard', prov_id=current_user.provider.id))
            elif current_user.is_customer:
                return redirect(url_for('customer.dashboard', cust_id=current_user.customer.id))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            
            if 'next' in session:
                next = session.get('next')
                if not next.startswith('/'):
                    next = url_for('core.home')
                session.pop('next', None)
                return redirect(next)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_provider:
                return redirect(url_for('provider.dashboard', prov_id=user.provider.id))
            else:
                return redirect(url_for('customer.dashboard', cust_id=user.customer.id))
        else:
            flash('Invalid credentials', category='error')

    return render_template('auth/login.html', form=form, role_enum=UserRoleEnum)



@auth.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    form = None

    if role == UserRoleEnum.CUSTOMER.value:
        form = CustomerRegisterForm()
    elif role == UserRoleEnum.PROVIDER.value:
        form = ProviderRegisterForm()
    else: 
        raise NotFound('No such role exists to register')
    
    if request.method == 'POST' and form.validate_on_submit():
        full_name = form.full_name.data
        username = form.username.data
        email = form.email.data
        gender = form.gender.data
        location = form.location.data
        contact = form.contact.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user:
            if user.profile.email == email:
                flash('user already exists', category='error')
                return redirect(url_for('auth.login'))
            flash('username already exist', category='error')
        else:
            try:
                new_user = User(username=username)
                new_user.password = password

                profile = Profile(full_name=full_name, email=email, gender=gender, location=location, contact=contact)
                new_user.profile = profile
                
                if role == UserRoleEnum.CUSTOMER.value:
                    new_user.role = UserRoleEnum.CUSTOMER.value
                    new_customer = Customer()
                    new_user.customer = new_customer
                    flash('customer registered successfully', category='success')
                elif role == UserRoleEnum.PROVIDER.value:
                    category_name = form.category.data
                    experience = form.experience.data

                    new_user.role = UserRoleEnum.PROVIDER.value
                    new_provider = Provider(experience=int(experience))
                    new_user.provider = new_provider
                    category_obj = Category.query.filter_by(name=category_name).first()

                    if category_obj:
                        category_obj.providers.append(new_provider)
                    flash('provider registered successfully', category='success')
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('auth.login')) 
            except Exception as e:
                db.session.rollback()  
                raise InternalServerError(f'Something went wrong while registering {role}')
    return render_template('auth/register.html', form=form, role=role, role_enum=UserRoleEnum)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/fresh')
@fresh_login_required
def fresh():
    return '<h2>Fresh Page</h2>'
