from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from config import Config

from extensions import db  # Импортируем db из extensions.py
from models import User, TestResult  # Импортируем модели
from forms import RegistrationForm, LoginForm  # Убедитесь, что импортируете формы

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # Инициализируем db с приложением

login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)


# Настройка менеджера входа
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Указание, что представление 'login' отвечает за вход пользователя

# Функция сохранения результатов в базу данных через SQLAlchemy
def save_to_database(result):
    new_result = TestResult(
        test_type=result['test_type'],
        result_data=str(result['data']),
        is_verified=result['is_verified'],
        user_id=current_user.id  # Привязываем результат к текущему пользователю
    )
    db.session.add(new_result)
    db.session.commit()

# Функция загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Главная страница с выбором тестов
@app.route('/')
def index():
    return render_template('index.html')

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    message = ''
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            message = 'Неправильный логин или пароль'
    return render_template('login.html', form=form, message=message)

# Выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Страница теста HADS
@app.route('/hads-test')
@login_required
def hads_test():
    return render_template('hads_test.html')

# Обработка теста HADS
@app.route('/submit-hads', methods=['POST'])
@login_required
def submit_hads():
    anxiety_scores = [int(request.form[f'anxiety_{i}']) for i in range(1, 8)]
    depression_scores = [int(request.form[f'depression_{i}']) for i in range(1, 8)]

    total_anxiety = sum(anxiety_scores)
    total_depression = sum(depression_scores)

    is_verified = request.form.get('is_verified') == 'true'

    result = {
        'test_type': 'HADS',
        'data': {
            'total_anxiety': total_anxiety,
            'total_depression': total_depression
        },
        'is_verified': is_verified
    }

    save_to_database(result)
    return jsonify({'status': 'success', 'total_anxiety': total_anxiety, 'total_depression': total_depression})

# Страница теста C-SSRS
@app.route('/c-ssrs-test')
@login_required
def c_ssrs_test():
    return render_template('c_ssrs_test.html')

# Обработка теста C-SSRS
@app.route('/submit-c-ssrs', methods=['POST'])
@login_required
def submit_cssrs():
    answers = {
        'q1': request.form.get('question_1'),
        'q2': request.form.get('question_2')
    }

    high_risk = answers['q1'] == 'yes' or answers['q2'] == 'yes'

    is_verified = request.form.get('is_verified') == 'true'

    result = {
        'test_type': 'C-SSRS',
        'data': answers,
        'is_verified': is_verified
    }

    save_to_database(result)
    return jsonify({'status': 'success', 'high_risk': high_risk})

# Страница теста TSQ
@app.route('/ptsd-test')
@login_required
def ptsd_test():
    return render_template('ptsd_test.html')

# Обработка теста TSQ
@app.route('/submit-ptsd', methods=['POST'])
@login_required
def submit_ptsd():
    answers = [request.form.get(f'q{i}') for i in range(1, 11)]
    total_score = sum([1 if ans == 'yes' else 0 for ans in answers])
    is_verified = request.form.get('is_verified') == 'true'

    result = {
        'test_type': 'TSQ',
        'data': {
            'total_score': total_score,
            'answers': answers
        },
        'is_verified': is_verified
    }

    save_to_database(result)
    return jsonify({'status': 'success', 'total_score': total_score})

if __name__ == '__main__':
    app.run()
