from flask import Blueprint
from flask_restful import Api


bp = Blueprint('api', __name__)



@bp.errorhandler(409)
def conflict(error):
    return {'msg': 'nlsknlsknbs'}, 409

@bp.app_errorhandler(500)
def internal(error):
    print('dnknkbnksnb')
    return {'msg': 'nlsknlsknbs'}, 500


from .apis import api
