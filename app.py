from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

# JWT 설정
app.config["JWT_SECRET_KEY"] = "I'M IML"
jwt = JWTManager(app)

# 데이터베이스 대신 사용할 간단한 사용자 데이터 저장소 (딕셔너리)
# 실제 애플리케이션에서는 데이터베이스(SQLite, PostgreSQL 등)를 사용합니다.
users = {}

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        if user_id in users and check_password_hash(users[user_id]['password'], password):

            # 세션 로그인
            session['user_id'] = user_id

            # JWT 토큰 생성
            access_token = create_access_token(identity=user_id)
            session['access_token'] = access_token

            flash('로그인에 성공했습니다!', 'success')
            return redirect(url_for('welcome'))

        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = request.form['email']

        if user_id in users:
            flash('이미 존재하는 아이디입니다.', 'danger')
        elif password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users[user_id] = {'password': hashed_password, 'email': email}
            flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/findpassword', methods=['GET', 'POST'])
def findpassword():
    if request.method == 'POST':
        email = request.form['email']
        flash(f'{email} 주소로 비밀번호 재설정 링크를 보냈습니다. (실제 발송 x)', 'info')
        return redirect(url_for('findpassword'))
    return render_template('findPassword.html')


@app.route('/welcome')
def welcome():
    if 'user_id' in session:
        user_id = session['user_id']
        return render_template('welcome.html', user_id=user_id)
    else:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))


@app.route('/api/userinfo')
@jwt_required()
def userinfo():
    current_user = get_jwt_identity()
    return {"logged_in_user": current_user}


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('access_token', None)
    flash('성공적으로 로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)