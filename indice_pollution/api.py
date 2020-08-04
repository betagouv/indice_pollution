from flask import current_app, request, abort, jsonify
from datetime import datetime
from .regions.solvers import forecast as forecast_
from .autocomplete import autocomplete as autocomplete_

@current_app.route('/forecast')
def forecast():
    insee = request.args.get('insee')
    date = request.args.get('date') or str(datetime.today().date())

    try:
        forecast_getter = forecast_(insee)
    except KeyError:
        current_app.logger.error(f'INSEE {insee} not found')
        abort(404)

    return jsonify(forecast_getter(date=date, insee=insee))

@current_app.route('/autocomplete')
def autocomplete():
    q = request.args.get('q')

    return jsonify(autocomplete_(q))