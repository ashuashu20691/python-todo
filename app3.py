from flask import Flask, render_template, request, redirect, url_for
import cx_Oracle
import configparser
import os
from datetime import datetime

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

def get_db_connection():
    try:
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        return connection
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error connecting to the database: {error.message}")
        exit(1)

@app.route('/')
def index():
    base_url = request.base_url
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', todos=todos, base_url=base_url)

@app.route('/todo/<int:id>', methods=['GET'])
def todo_detail(id):
    base_url = request.base_url
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = :id", [id])
    todo = cursor.fetchone()
    cursor.close()
    connection.close()
    if todo:
        return render_template('todo_detail.html', todo=todo, base_url=base_url)
    return "Todo not found", 404

@app.route('/todo/new', methods=['GET', 'POST'])
def create_todo():
    base_url = request.base_url
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        completed = request.form.get('completed', 'N')
        due_date_str = request.form.get('due_date')  # New field

        # Parse date string to datetime object
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                return "Invalid date format. Use YYYY-MM-DD.", 400

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO todos (title, description, completed, due_date)
            VALUES (:title, :description, :completed, :due_date)
        """, [title, description, completed, due_date])
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))

    return render_template('todo_form.html', base_url=base_url)

@app.route('/todo/<int:id>/edit', methods=['GET', 'POST'])
def update_todo(id):
    base_url = request.base_url
    connection = get_db_connection()
    cursor = connection.cursor()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        completed = request.form.get('completed', 'N')
        due_date_str = request.form.get('due_date')  # New field

        # Parse date string to datetime object
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                return "Invalid date format. Use YYYY-MM-DD.", 400

        cursor.execute("""
            UPDATE todos
            SET title = :title,
                description = :description,
                completed = :completed,
                due_date = :due_date
            WHERE id = :id
        """, [title, description, completed, due_date, id])
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM todos WHERE id = :id", [id])
    todo = cursor.fetchone()
    cursor.close()
    connection.close()
    if todo:
        return render_template('todo_form.html', todo=todo, base_url=base_url)
    return "Todo not found", 404

@app.route('/todo/<int:id>/delete', methods=['POST'])
def delete_todo(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM todos WHERE id = :id", [id])
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    base_url = request.base_url
    connection = get_db_connection()
    cursor = connection.cursor()

    # Get total count of todos
    cursor.execute("SELECT COUNT(*) FROM todos")
    total_todos = cursor.fetchone()[0]

    # Get count of completed todos
    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 'Y'")
    completed_todos = cursor.fetchone()[0]

    # Get count of incomplete todos
    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 'N'")
    incomplete_todos = cursor.fetchone()[0]

    # Get recent todos
    cursor.execute("SELECT * FROM todos ORDER BY created_at DESC FETCH FIRST 5 ROWS ONLY")
    recent_todos = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('dashboard.html', 
                           base_url=base_url, 
                           total_todos=total_todos,
                           completed_todos=completed_todos,
                           incomplete_todos=incomplete_todos,
                           recent_todos=recent_todos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


