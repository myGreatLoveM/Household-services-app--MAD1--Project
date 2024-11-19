from flask import Blueprint


provider = Blueprint('provider', __name__)

from . import views
