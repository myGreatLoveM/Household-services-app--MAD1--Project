from flask import Blueprint, render_template


admin = Blueprint('admin', __name__)


from . import views