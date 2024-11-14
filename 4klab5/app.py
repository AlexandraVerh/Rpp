from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, logout_user, current_user
from models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

# Пример пользователя
users = {'user1@example.com': User('1', 'user1@example.com', 'password1', 'User One')}

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
    return redirect(url_for('index'))

@app.route('/login')
def login():
    # Здесь должна быть логика для обработки входа пользователя
    # Для простоты, авторизуем пользователя по умолчанию
    user = users.get('user1@example.com')
    if user:
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
