from flask import render_template, Blueprint, request, make_response, jsonify
from . import core

@core.app_errorhandler(404)
def page_not_found(err: Exception):
    return render_template('errors/404.html', err=err), 404

@core.app_errorhandler(403)
def forbidden(err: Exception):
    return render_template('errors/403.html', err=err), 403

@core.app_errorhandler(500)
def internal_server_error(err: Exception):
    return render_template('errors/500.html', err=err), 500


# @main.app_errorhandler(403)
# def forbidden(e):
#     if request.accept_mimetypes.accept_json and \
#             not request.accept_mimetypes.accept_html:
#         response = jsonify({'error': 'forbidden'})
#         response.status_code = 403
#         return response
#     return render_template('403.html'), 403


# @main.app_errorhandler(404)
# def page_not_found(e):
#     if request.accept_mimetypes.accept_json and \
#             not request.accept_mimetypes.accept_html:
#         response = jsonify({'error': 'not found'})
#         response.status_code = 404
#         return response
#     return render_template('404.html'), 404


# @main.app_errorhandler(500)
# def internal_server_error(e):
#     if request.accept_mimetypes.accept_json and \
#             not request.accept_mimetypes.accept_html:
#         response = jsonify({'error': 'internal server error'})
#         response.status_code = 500
#         return response
#     return render_template('500.html'), 500




# from flask import render_template, request
# from app import db
# from app.errors import bp
# from app.api.errors import error_response as api_error_response


# def wants_json_response():
#     return request.accept_mimetypes['application/json'] >= \
#         request.accept_mimetypes['text/html']


# @bp.app_errorhandler(404)
# def not_found_error(error):
#     if wants_json_response():
#         return api_error_response(404)
#     return render_template('errors/404.html'), 404


# @bp.app_errorhandler(500)
# def internal_error(error):
#     db.session.rollback()
#     if wants_json_response():
#         return api_error_response(500)
#     return render_template('errors/500.html'), 500