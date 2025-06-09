from app import app, db
from sqlalchemy import text  # import text

def cek_kolom_ada():
    with app.app_context():
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(resep)")).fetchall()  # pake text()
            kolom = [row[1] for row in result]
            return 'diposting_oleh' in kolom

def tambah_kolom():
    with app.app_context():
        if cek_kolom_ada():
            print("Kolom 'diposting_oleh' sudah ada, tidak perlu ditambahkan lagi.")
            return
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE resep ADD COLUMN diposting_oleh TEXT"))  # pake text()
            print("Kolom 'diposting_oleh' berhasil ditambahkan.")

if __name__ == '__main__':
    tambah_kolom()
