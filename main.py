from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# --- File Paths ---
USERS_FILE = 'users.json'
TASKS_FILE = 'tasks.json'

# --- Data Loading and Saving Functions ---

def load_data(file_path):
    """Loads JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, file_path):
    """Saves data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# --- Load initial data ---
users = load_data(USERS_FILE)
tasks = load_data(TASKS_FILE)

# A simple global counter for unique task IDs
task_id_counter = 1
# To ensure the counter starts after the highest existing ID
if tasks and isinstance(tasks, dict):
    all_tasks = [task for user_tasks in tasks.values() for task in user_tasks]
    if all_tasks:
        task_id_counter = max(task['id'] for task in all_tasks) + 1


# --- Routes ---

@app.route('/')
def home():
    return 'Welcome! <a href="/login">Login</a> or <a href="/register">Register</a>'

@app.route('/register', methods=['GET', 'POST'])
def register():
    global users, tasks
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # --- CORRECTED SECTION START ---
        # Ensure 'users' is a dictionary to prevent crashing if users.json is a list
        if not isinstance(users, dict):
            users = {}
        # --- CORRECTED SECTION END ---

        if username in users:
            return "Username already exists!", 400

        users[username] = password
        # Ensure tasks is a dictionary before assigning
        if not isinstance(tasks, dict):
            tasks = {}
        tasks[username] = []  # Initialize an empty task list for the new user

        save_data(users, USERS_FILE)
        save_data(tasks, TASKS_FILE)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if users.get(username) == password:
            return redirect(url_for('dashboard', username=username))
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    user_tasks = tasks.get(username, []) if isinstance(tasks, dict) else []
    return render_template('dashboard.html', username=username, tasks=user_tasks)

@app.route('/add/<username>', methods=['POST'])
def add_task(username):
    global task_id_counter, tasks
    task_name = request.form.get('task_name')
    task_date = request.form.get('task_date')

    if isinstance(tasks, dict) and task_name and task_date and username in tasks:
        tasks[username].append({
            "id": task_id_counter,
            "name": task_name,
            "date": task_date
        })
        task_id_counter += 1
        save_data(tasks, TASKS_FILE)

    return redirect(url_for('dashboard', username=username))

@app.route('/delete/<username>/<int:task_id>')
def delete_task(username, task_id):
    global tasks
    if isinstance(tasks, dict) and username in tasks:
        tasks[username] = [task for task in tasks[username] if task['id'] != task_id]
        save_data(tasks, TASKS_FILE)

    return redirect(url_for('dashboard', username=username))


if __name__ == '__main__':
    app.run(debug=True)