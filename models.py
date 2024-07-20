from app import db

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    entry_type = db.Column(db.String(10), nullable=False)  # 'Entrada' ou 'Saída'
