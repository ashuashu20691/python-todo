from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from sqlalchemy.pool import NullPool
import os
import cx_Oracle
import configparser

app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('config.cfg')

# Database configuration details
config = configparser.ConfigParser()
config.read('config.cfg')

# Oracle database configuration
username = config['database']['ADB_USER']
password = config['database']['ADB_PASSWORD']
dsn = config['database']['TNS_SERVICE_NAME']
wallet_path = config['database']['TNS_ADMIN']

# Set the TNS_ADMIN environment variable to the wallet directory path
os.environ['TNS_ADMIN'] = wallet_path

# Configure session pool to connect to the database
pool = cx_Oracle.SessionPool(user=username, password=password, dsn=dsn, min=2, max=2, increment=0, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)

def mycreator():
    return pool.acquire(cclass="MYCLASS", purity=cx_Oracle.ATTR_PURITY_SELF)

app.config['SQLALCHEMY_DATABASE_URI'] = "oracle://"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"creator": mycreator, "poolclass": NullPool, "max_identifier_length": 128}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise
db = SQLAlchemy(app)

# Test the SQLAlchemy connection
try:
    with db.engine.connect() as connection:
        print("Connected to the database with SQLAlchemy successfully.")
except Exception as e:
    print(f"Error connecting to the database with SQLAlchemy: {e}")
    exit(1)



class Todo(db.Model):
    id = db.Column(db.Integer, db.Identity(start=3), primary_key=True)
    task = db.Column(db.String(1000), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)

@app.route('/todolist')
def index():
    try:
        with cx_Oracle.connect(user=username, password=password, dsn=dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM expenses")
                result = cursor.fetchall()
                print("Query result:", result)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error connecting to the database: {error.message}")
    
    todoList = Todo.query.all()
    base_url = request.base_url
    return render_template('base.html', todo_list=todoList)

@app.route('/todolist/imagemap')
def index1():
    todoList = Todo.query.all()
    base_url = request.base_url
    return render_template('imagemap.html', todo_list=todoList)

# Add a task
@app.route('/todolist/add', methods=["POST"])
def add():
    title = request.form.get("title")
    if title == "":
        return redirect(url_for("index"))

    newTask = Todo(task=title, complete=False)
    try:
        db.session.add(newTask)
        db.session.commit()
        return redirect(url_for("index"))
    except exc.SQLAlchemyError as e:
        print(type(e))
        error = str(e.__dict__['orig'])
        return error

# Delete a task
@app.route('/todolist/delete/<int:todo_id>')
def delete(todo_id):
    task = Todo.query.filter_by(id=todo_id).first()
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was an issue deleting your task."

# Update a task
@app.route('/todolist/update/<int:todo_id>')
def update(todo_id):
    task = Todo.query.filter_by(id=todo_id).first()
    task.complete = not task.complete
    try:
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was an issue deleting your task."

# Print URL
@app.route('/todolist/foo2')
def foo():
    return request.base_url + ' is the url\n'

if __name__ == "__main__":
    app.config.from_pyfile('config.cfg')
    db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

