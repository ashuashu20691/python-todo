from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import cx_Oracle
import os
import configparser

app = Flask(__name__)

# Read configuration from config.cfg
config = configparser.ConfigParser()
config.read('config.cfg')

# Oracle database configuration
username = config['database']['USER']
password = config['database']['PASSWORD']
dsn = config['database']['TNS_SERVICE_NAME']
wallet_path = config['database']['TNS_ADMIN']

# Set the TNS_ADMIN environment variable to the wallet directory path
os.environ['TNS_ADMIN'] = wallet_path

# Attempt to connect to the database
try:
    with cx_Oracle.connect(user=username, password=password, dsn=dsn) as connection:
        print("Connected to the database successfully.")
except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"Error connecting to the database: {error.message}")

    # Exit the application or handle the error as needed
    exit(1)


# Database URI for SQLAlchemy
DB_URI = f"oracle+cx_oracle://{username}:{password}@{dsn}?encoding=UTF-8&nencoding=UTF-8"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Test the SQLAlchemy connection
try:
    with db.engine.connect() as connection:
        print("Connected to the database with SQLAlchemy successfully.")
except Exception as e:
    print(f"Error connecting to the database with SQLAlchemy: {e}")
    exit(1)


# Define Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(1000), nullable=False)
    complete = db.Column(db.Boolean, default=False)

# Create tables based on defined models
@app.before_first_request
def setup():
    print("calling setup")
    db.create_all()

# Route for rendering index page with task list
@app.route('/')
def index():
    print("query all")
    todo_list = Todo.query.all()
    return render_template('index.html', todo_list=todo_list)

# Route for adding a new task
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    new_task = Todo(task=title)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

# Route for updating a task (mark as complete or incomplete)
@app.route('/update/<int:task_id>')
def update(task_id):
    task = Todo.query.get(task_id)
    task.complete = not task.complete
    db.session.commit()
    return redirect(url_for('index'))

# Route for deleting a task
@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Todo.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("app start........")
    app.run(debug=True,host='0.0.0.0')

