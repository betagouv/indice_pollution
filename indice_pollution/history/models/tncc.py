from indice_pollution.extensions import db

class TNCC:
    tncc = db.Column(db.Integer)
    tncc_codes= {
        0: {"article": " ",    "charniere": "de "},
        1: {"article": " ", 	  "charniere": "d'"},
        2: {"article": "le ",  "charniere": "du "},
        3: {"article": "la ",  "charniere": "de la "},
        4: {"article": "les ", "charniere": "des "},
        5: {"article": "l’",  "charniere": "de l’"},
        6: {"article": "aux ", "charniere": "des "},
        7: {"article": "las ", "charniere": "de las "},
        8: {"article": "los ", "charniere": "de los "}
    }

    def nom_charniere(self):
        return f"{self.tncc_codes[self.tncc]['charniere']}{self.nom}"