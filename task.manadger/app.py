from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import sqlite3

connection = sqlite3.connect("task_manager.db", check_same_thread=False)

app = Flask(__name__)
app.secret_key = "123456789"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/taskAdd')
def taskAdd():
    return render_template('taskAdd.html')


@app.route('/reg', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('reg.html', message="All fields are required.")

        user = get_user(username)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('tasks'))
        else:
            return render_template('reg.html', message="Invalid username or password.")

    return render_template('reg.html')


@app.route('/auth', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if not username or not password or not confirm_password:
            return render_template('auth.html', message="All fields are required.")

        if password != confirm_password:
            return render_template('auth.html', message="Passwords do not match.")

        if len(password) < 6:
            return render_template('auth.html', message="Password must be at least 6 characters long.")

        try:
            add_user(username, password)

            user = get_user(username)

            session['user_id'] = user['id']
            session['username'] = username

            return redirect(url_for('index'))

        except ValueError as e:
            return render_template('auth.html', message=str(e))

    return render_template('auth.html')


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('register'))

    user_id = session['user_id']

    if request.method == 'POST':
        title = request.form.get('taskTitle')
        description = request.form.get('taskDescription')
        due_date = request.form.get('due_date')

        if not title or not description or not due_date:
            return "All fields are required!"
        add_task(user_id, title, description, due_date)
        return redirect(url_for('tasks'))

    user_tasks = get_tasks(user_id)
    return render_template('tasks.html', tasks=user_tasks)


@app.route('/delete')
def delete_task():
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row
    id = request.args.get('id')
    cursor.execute('''delete from tasks where id = ?''', (id,))
    connection.commit()
    return redirect('/tasks')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# -------------------------------------------------------------------

def get_user(username):
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    return user


def add_user(username, password):
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Имя пользователя уже существует.")
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        raise

def add_task(user_id, title, description, date):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (user_id, title, description, date, completed)
        VALUES (?, ?, ?, ?, 0)
        """, (user_id, title, description, date))
    connection.commit()
    return 'Сохранено'


def get_tasks(user_id):
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    return tasks




if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
