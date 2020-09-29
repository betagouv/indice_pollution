try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    db = None
else:
    db = SQLAlchemy()