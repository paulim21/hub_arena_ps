"""Extensões compartilhadas da aplicação.

O objeto `db` (Flask-SQLAlchemy) é criado aqui — sem vínculo com a app —
para que Models, Repositories e Services possam importá-lo sem import circular.
A ligação com a aplicação acontece em `app.py`, via `db.init_app(app)`.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
