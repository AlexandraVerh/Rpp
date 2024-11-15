from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

# Пример пользователей
users = {}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = next((u for u in users.values() if u.email == email), None)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверный адрес электронной почты или пароль')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if email in users:
            flash('Пользователь уже существует')
        else:
            user_id = str(len(users) + 1)
            new_user = User(user_id, email, password, name)
            users[user_id] = new_user
            flash('Пользователь успешно зарегистрирован')
            return redirect(url_for('login'))
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)


