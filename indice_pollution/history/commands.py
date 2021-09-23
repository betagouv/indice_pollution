from indice_pollution import today
from indice_pollution.history.models import IndiceHistory
from flask import current_app
from datetime import timedelta

@current_app.cli.command('prune-history')
def prune_history():
    date_ = today() - timedelta(days=7)
    IndiceHistory.query.filter(IndiceHistory.date_ <= date_).delete()
    current_app.logger.info(f'Data before {date_} is removed from history')
