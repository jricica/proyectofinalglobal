from flask import Flask, request, jsonify, make_response, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta
from functools import wraps
import threading
from jwt.exceptions import ExpiredSignatureError
import secrets

app = Flask(__name__)
app.config["SECRET_KEY"] = "32ddaaffe3894d8dac05c62de02453ñ"
# Configuración de la primera base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_BINDS"] = {
    'users': 'sqlite:///users.db',
    'logs': 'sqlite:///logs.db'
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Definir modelo para los registros de ingreso y logout
class Log(db.Model):
    __bind_key__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Log('{self.event}', '{self.user_id}', '{self.timestamp}')"

# Modelo para los tokens utilizados
class UsedToken(db.Model):
    __bind_key__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), unique=True, nullable=False)

# Modelo para los usuarios
class User(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User('{self.fullname}', '{self.email}', '{self.username}')"

# Modelo para los detalles del usuario
class UserDetails(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(100))
    phone_number = db.Column(db.String(20), nullable=True)  # Permitir valores nulos

    # Relación con el modelo User
    user = db.relationship('User', backref=db.backref('details', uselist=False))

    def __repr__(self):
        return f"UserDetails('{self.user_id}', '{self.address}', '{self.phone_number}')"

# Función decoradora para requerir token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        
        if not token:
            return redirect(url_for('home'))
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except ExpiredSignatureError:
            # Si el token ha expirado, eliminar las variables de sesión y redirigir a la página de inicio de sesión
            session.pop('logged_in', None)
            session.pop('token', None)
            return redirect(url_for('home'))
        except jwt.InvalidTokenError:
            return redirect(url_for('logout_user'))
        
        # Verificar si el token ya ha sido utilizado
        if UsedToken.query.filter_by(token=token).first():
            return redirect(url_for('logout_user'))  # Redirigir si el token ya ha sido utilizado
        
        return f(*args, **kwargs)
    return decorated

# Función para generar una nueva clave secreta
def generate_secret_key():
    return secrets.token_urlsafe(32)

# Función para iniciar el temporizador para el token
def start_token_timer():
    token = session.get('token')
    if token:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        expiration_time = datetime.utcfromtimestamp(data['exp'])
        duration = (expiration_time - datetime.utcnow()).total_seconds()
        threading.Timer(duration, logout_user).start()

# Función para calcular el tiempo restante antes del cierre de sesión automático
def remaining_time():
    token = session.get('token')
    if token:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        expiration_time = datetime.utcfromtimestamp(data['exp'])
        remaining = expiration_time - datetime.utcnow()
        return max(remaining, timedelta(0))
    return timedelta(0)

# Ruta pública
@app.route("/public")
def public():
    return jsonify({'message': 'This is a public page!'})

# Ruta autenticada
@app.route("/auth")
@token_required
def auth():
    return jsonify({'message': 'This is an authenticated page!'})

# Ruta principal
@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('user_dashboard'))

# Ruta del panel de usuario
@app.route("/user_dashboard")
def user_dashboard():
    if session.get('logged_in'):
        token = session.get('token')
        if token:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                # Si el token ha expirado, eliminar las variables de sesión y redirigir a la página de inicio de sesión
                session.pop('logged_in', None)
                session.pop('token', None)
                return redirect(url_for('home'))
            except jwt.InvalidTokenError:
                return redirect(url_for('logout_user'))
            
            # Registrar el token como utilizado
            used_token = UsedToken(token=token)
            db.session.add(used_token)
            db.session.commit()
            
            return render_template('user_dashboard.html', remaining_time=remaining_time())
    return redirect(url_for('home'))

# Ruta de inicio de sesión
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        session['logged_in'] = True
        
        # Generar nueva clave secreta
        new_secret_key = generate_secret_key()
        app.config["SECRET_KEY"] = new_secret_key
        
        token = jwt.encode({'user': user.email, 'exp': datetime.utcnow() + timedelta(seconds=60)}, new_secret_key, algorithm='HS256')
        session['token'] = token
        
        # Guardar registro de ingreso en la base de datos
        log = Log(event="login", user_id=user.email)
        db.session.add(log)
        db.session.commit()
        
        # Iniciar temporizador para el token
        start_token_timer()
        
        return redirect(url_for('user_dashboard'))
    else:
        return make_response('Could not verify!', 403, {'WWW-Authenticate': 'Basic realm="Login Required"'})

# Función para cerrar sesión de usuario
@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop('logged_in', None)
    session.pop('token', None)
    
    # Redirigir al usuario a la página principal
    return redirect(url_for('home'))

# Ruta de registro de usuario
@app.route("/register", methods=["POST"])
def register():
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    address = request.form.get("address")
    phone_number = request.form.get("phone_number")

    # Verificar si el correo electrónico ya está registrado
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return make_response("El correo electrónico ya está en uso", 400)

    # Verificar si el nombre de usuario ya está en uso
    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        return make_response("El nombre de usuario ya está en uso", 400)

    # Crear un nuevo usuario
    new_user = User(fullname=fullname, email=email, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    # Crear un nuevo registro de detalles de usuario
    new_user_details = UserDetails(user_id=new_user.id, address=address, phone_number=phone_number)
    db.session.add(new_user_details)
    db.session.commit()

    return redirect(url_for("home"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
