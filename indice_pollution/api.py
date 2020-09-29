from flask import current_app, request, abort, jsonify
from datetime import datetime
from . import forecast as forecast_
from .autocomplete import autocomplete as autocomplete_

@current_app.route('/forecast')
def forecast():
    insee = request.args.get('insee')
    date_ = request.args.get('date')

    try:
        result = forecast_(insee, date_)
    except KeyError as e:
        current_app.logger.error(f'INSEE {insee} not found')
        current_app.logger.error(e)
        abort(404)

    return jsonify(result)

@current_app.route('/autocomplete')
def autocomplete():
    q = request.args.get('q')

    return jsonify(autocomplete_(q))