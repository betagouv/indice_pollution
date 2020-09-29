from indice_pollution.regions.solvers import insee_list
from indice_pollution import forecast as forecast_, today
from indice_pollution.models import db
from indice_pollution.history.models import IndiceHistory
from flask import current_app
from datetime import timedelta

@current_app.cli.command('generate-history')
def generate_history():
    date_ = today()
    for insee in insee_list():
        current_app.logger.info(f'Getting history for {insee}')
        forecast_(insee, date_, force_from_db=True)

@current_app.cli.command('prune-history')
def prune_history():
    date_ = today() - timedelta(days=7)
    IndiceHistory.query.filter(IndiceHistory.date_ <= date_).delete()
    current_app.logger.info(f'Data before {date_} is removed from history')
