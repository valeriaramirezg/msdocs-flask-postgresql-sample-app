import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate


app = Flask(__name__, static_folder='static')
app.secret_key = 'key'
csrf = CSRFProtect(app)

from flask_wtf.csrf import generate_csrf

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

class ImageCloud(db.Model):
    __tablename__ = 'image_cloud'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    username = db.Column(db.Text, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    pixels = db.Column(db.Text, nullable=False)


from sqlalchemy.exc import ProgrammingError

@app.route('/', methods=['GET'])
def index():
    try:
        records = ImageCloud.query.all()
    except ProgrammingError:
        records = None  # Table doesn't exist yet
    return render_template('base.html', records=records)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/create-table', methods=['POST'])
def create_table():
    db.create_all()
    return redirect(url_for('index'))

#   AÑADIR ENTRY DE PRUEBA A LA BASE DE DATOS
@app.route('/add-entry', methods=['POST'])
def add_entry():
    new_entry = ImageCloud(
        date=datetime.now().date(),
        username='test_user',
        filename='example.png',
        pixels='1920x1080'
    )
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for('index'))

from flask import jsonify

#   AÑADIR ENTRY DESDE FUERA
@app.route('/api/add-entry', methods=['POST'])
@csrf.exempt  # Desactiva CSRF solo para este endpoint API externo
def api_add_entry():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON payload provided'}), 400
    
    try:
        new_entry = ImageCloud(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            username=data['username'],
            filename=data['filename'],
            pixels=data['pixels']
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({'message': 'Entry added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
