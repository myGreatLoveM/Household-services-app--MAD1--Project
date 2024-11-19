from flask import abort, redirect, request, session, url_for, flash
from flask_login import current_user, logout_user
from functools import wraps
from application.core.enums import UserRoleEnum
from werkzeug.exceptions import Forbidden


def role_required(role_name):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role_name:
                logout_user()
                raise Forbidden('Access Denied: You don’t have permission to view this page.')

            if current_user.is_authenticated and current_user.is_customer:
                if current_user.customer.id != kwargs.get('cust_id'):
                    logout_user()
                    raise Forbidden('Access Denied: You don’t have permission to view this page.')
                if current_user.customer.is_blocked:
                    logout_user()
                    raise Forbidden('Oops! You have been blocked by admin')

            elif current_user.is_authenticated and current_user.is_provider:
                if current_user.provider.id != kwargs.get('prov_id'):
                    logout_user()
                    raise Forbidden('Access Denied: You don’t have permission to view this page.')
                if current_user.provider.is_blocked:
                    logout_user()
                    raise Forbidden('Oops! You have been blocked by admin')
            return f(*args, **kwargs)
        return decorated_function
    return wrapper