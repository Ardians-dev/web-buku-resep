from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Pengguna(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    resep = db.relationship('Resep', backref='pengguna', lazy=True)
    
class Resep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul_resep = db.Column(db.String(150), nullable=False)
    deskripsi_resep = db.Column(db.String(6000), nullable=False)
    bahan_resep = db.Column(db.String(6000), nullable=False)
    langkah_langkah = db.Column(db.String(6000), nullable=False)
    diposting_oleh = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('pengguna.id'), nullable=False)