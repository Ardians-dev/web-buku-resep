from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from groq import Groq
from models import db, Pengguna, Resep

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resep.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Pengguna.query.get(int(user_id))

with app.app_context():
    db.create_all()


ai_key = "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"
client = Groq(api_key=ai_key)

chat_history = []

@app.route("/chat_ai", methods=["GET", "POST"])
def chat():
    global chat_history

    if request.method == "POST":
        user_input = request.form["message"]
        chat_history.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                messages=chat_history,
                model="llama3-8b-8192",
                stream=False,
            )
            ai_reply = response.choices[0].message.content
        except Exception:
            ai_reply = "Maaf, AI sedang sibuk."

        chat_history.append({"role": "assistant", "content": ai_reply})
        return redirect(url_for("chat"))

    return render_template("grock_ai.html", chat_history=chat_history)

@app.route('/')
def index():
    return redirect(url_for('manajemen_resep')) if current_user.is_authenticated else redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if Pengguna.query.filter_by(username=username).first():
            flash('username sudah digunakan, coba gunakan nama lain')
            return redirect(url_for('register'))
        new_user = Pengguna(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('registrasi berhasil, silakan login')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pengguna = Pengguna.query.filter_by(username=request.form['username']).first()
        if pengguna and check_password_hash(pengguna.password, request.form['password']):
            login_user(pengguna)
            return redirect(url_for('manajemen_resep'))
        flash('username atau password salah')
    return render_template('/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/manajemen_resep')
def manajemen_resep():
    return render_template('manajemen_resep.html')

@app.route('/daftar_resep')
def daftar_resep():
    daftar_resep = Resep.query.all()
    return render_template('daftar_resep.html', daftar_resep=daftar_resep)

@app.route('/detail_resep/<int:id>')
def detail_resep(id):
    detaill_resep = Resep.query.get_or_404(id)
    return render_template('detail_resep.html', detaill_resep=detaill_resep, current_user=current_user)

@app.route('/tambah_resep', methods=['GET', 'POST'])
@login_required
def tambah_resep():
    if request.method == 'POST':
        judul_resep = request.form['judul_resep']
        deskripsi_resep = request.form['deskripsi_resep']
        bahan_resep = request.form['bahan_resep']
        langkah_langkah = request.form['langkah_langkah']
        diposting_oleh = request.form['diposting_oleh']
        new_resep = Resep(judul_resep=judul_resep, deskripsi_resep=deskripsi_resep, bahan_resep=bahan_resep, langkah_langkah=langkah_langkah, diposting_oleh=diposting_oleh, pengguna=current_user)
        db.session.add(new_resep)
        db.session.commit()
        return redirect(url_for('daftar_resep'))
    return render_template('tambah_resep.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    resep_asli = Resep.query.get(id)
    resep = Resep.query.get_or_404(id)
    if request.method == 'POST':
        resep.judul_resep = request.form['judul_resep']
        resep.deskripsi_resep = request.form['deskripsi_resep']
        resep.bahan_resep = request.form['bahan_resep']
        resep.langkah_langkah = request.form['langkah_langkah']
        resep.diposting_oleh = request.form['diposting_oleh']
        db.session.commit()
        return redirect(url_for('daftar_resep'))
    return render_template('edit_resep.html', resep=resep, resep_asli=resep_asli)

@app.route('/hapus/<int:id>')
@login_required
def hapus(id):
    resep = Resep.query.get_or_404(id)
    if resep.user_id != current_user.id:
        flash('akses ditolak')
        return redirect(url_for('daftar_resep'))
    db.session.delete(resep)
    db.session.commit()
    return redirect(url_for('daftar_resep'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)