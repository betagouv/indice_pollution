from indice_pollution.history.models.indice_atmo import IndiceATMO
from datetime import date

def test_get(db_session, commune_commited):
    date_ = date(2022, 4, 25)
    db_session.add(IndiceATMO(
        zone_id=commune_commited.zone_id,
        date_ech=date_,
        date_dif=date_,
        no2=1,
        so2=1,
        o3=1,
        pm10=1,
        pm25=1,
        valeur=1
    ))
    db_session.commit()
    indice = IndiceATMO.get(insee=commune_commited.insee, date_=date_)
    assert indice
    assert indice.zone_id == commune_commited.zone_id