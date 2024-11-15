from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456987'

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
        if user and user.check_password(password):
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

        # Проверяем, существует ли пользователь с таким email
        existing_user = next((u for u in users.values() if u.email == email), None)
        if existing_user:
            flash('Пользователь уже существует')
        else:
            user_id = str(len(users) + 1)
            new_user = User(user_id, email, password, name)
            users[user_id] = new_user
            flash('Пользователь успешно зарегистрирован')
            return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/users')
@login_required
def users_list():
    return render_template('users.html', users=users.values())


if __name__ == '__main__':
    app.run(debug=True)
