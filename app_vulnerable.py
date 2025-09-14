from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

DATABASE = 'vuln_database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    # 쿼리 결과를 딕셔너리 형태로 받기 위해 row_factory 설정
    db.row_factory = sqlite3.Row
    return db

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

        db = get_db()
        cursor = db.cursor()

        # ===============================================================
        # !!! 1번 취약점: SQL 인젝션 (SQL Injection) !!!
        # 사용자의 입력값을 아무런 검증 없이 그대로 쿼리문에 합쳐버립니다.
        # 공격자가 이 부분을 악용하여 데이터베이스를 조작할 수 있습니다.
        # ===============================================================
        query = f"SELECT * FROM users WHERE user_id = '{user_id}' AND password = '{password}'"
        
        try:
            # .execute()는 기본적으로 하나의 SQL문만 실행하지만,
            # 쿼리 자체를 조작하는 기본적인 SQL 인젝션 공격에는 매우 취약합니다.
            cursor.execute(query)
            user = cursor.fetchone()
        except Exception as e:
            print(f"데이터베이스 오류: {e}")
            user = None

        db.close()

        if user:
            session['user_id'] = user['user_id']
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
        email = request.form['email']

        db = get_db()
        cursor = db.cursor()

        try:
            # ===============================================================
            # !!! 2번 취약점: 안전하지 않은 비밀번호 저장 !!!
            # 사용자가 입력한 비밀번호를 암호화하지 않고 그대로 데이터베이스에 저장합니다.
            # 데이터베이스가 유출되면 모든 사용자의 비밀번호가 노출됩니다.
            # ===============================================================
            cursor.execute("INSERT INTO users (user_id, password, email) VALUES (?, ?, ?)", 
                           (user_id, password, email))
            db.commit()
            flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('이미 존재하는 아이디입니다.', 'danger')
        finally:
            db.close()

    return render_template('signup.html')


# welcome, logout, findpassword 라우트는 기능이 동일하여 그대로 사용합니다.
@app.route('/findpassword', methods=['GET', 'POST'])
def findpassword():
    if request.method == 'POST':
        email = request.form['email']
        flash(f'{email} 주소로 비밀번호 재설정 링크를 보냈습니다. (실제 발송은 안됨)', 'info')
        return redirect(url_for('findpassword'))
    return render_template('findPassword.html')

@app.route('/welcome')
def welcome():
    if 'user_id' in session:
        return render_template('welcome.html', user_id=session['user_id'])
    else:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('성공적으로 로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

