from enum import Enum


class UserRoleEnum(Enum):
    ADMIN = 'admin'
    PROVIDER = 'provider'
    CUSTOMER = 'customer'


# role = request.args.get('role', default='customer', type=str)





avatar = "https://avatar.iran.liara.run/public/boy?username={}"


from flask import abort, redirect, url_for, flash
from flask_login import current_user
from functools import wraps


def role_required(role_name):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(current_user.role, role_name)
            if current_user.role != role_name:
                flash('Not authorized')
                return redirect(url_for('auth.logout'))
            
            if current_user.role == UserRoleEnum.CUSTOMER.value:
                if current_user.customer.id != kwargs.get('cust_id'):
                    flash('Not authorized')
                    return redirect(url_for('auth.logout'))
            elif current_user.role == UserRoleEnum.PROVIDER.value:
                if current_user.provider.id != kwargs.get('prov_id'):
                    flash('Not authorized')
                    return redirect(url_for('auth.logout'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


# def roles_required(*role_names):
#     def wrapper(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if not current_user.is_authenticated:
#                 return login_manager.unauthorized()
#             if not any(role.name in role_names for role in current_user.roles):
#                 abort(403)  # Forbidden access
#             return f(*args, **kwargs)
#         return decorated_function
#     return wrapper


# def brand_required(func):
#     @wraps(func)
#     def inner(*args, **kwargs):
#         if current_user and not current_user.is_brand:
#             return redirect(url_for('auth.logout'))
#         if (kwargs['brand_id'] != current_user.brand.id):
#             return redirect(url_for('auth.logout'))
#         return func(*args, **kwargs)
#     return inner


# naming_convention={
#         "ix": 'ix_%(column_0_label)s',
#         "uq": "uq_%(table_name)s_%(column_0_name)s",
#         "ck": "ck_%(table_name)s_%(constraint_name)s",
#         "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#         "pk": "pk_%(table_name)s"
#     }