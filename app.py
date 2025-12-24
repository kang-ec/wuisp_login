from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies,
    get_jwt
)
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", os.urandom(32))
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_ENV")

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = True

app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token_cookie"

jwt = JWTManager(app)

users = {}

revoked_jti = set()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    return jti in revoked_jti


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]
        email = request.form["email"]

        if user_id in users:
            flash("이미 존재하는 아이디입니다.", "danger")
        elif password != password_confirm:
            flash("비밀번호가 일치하지 않습니다.", "danger")
        else:
            users[user_id] = {
                "password": generate_password_hash(password),
                "email": email
            }
            flash("회원가입이 완료되었습니다! 로그인해주세요.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        if user_id in users and check_password_hash(users[user_id]["password"], password):
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)

            resp = redirect(url_for("welcome"))
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)

            flash("로그인에 성공했습니다!", "success")
            return resp

        flash("아이디 또는 비밀번호가 올바르지 않습니다.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/welcome")
@jwt_required()  # access token 필요
def welcome():
    user_id = get_jwt_identity()
    return render_template("welcome.html", user_id=user_id)


@app.route("/api/userinfo")
@jwt_required()
def userinfo():
    current_user = get_jwt_identity()
    return jsonify(logged_in_user=current_user)


@app.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)  # refresh token 필요
def refresh():
    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id)

    resp = jsonify(message="access token refreshed")
    set_access_cookies(resp, new_access)
    return resp


@app.route("/logout", methods=["POST", "GET"])
@jwt_required(optional=True)
def logout():
    try:
        jwt_data = get_jwt()
        jti = jwt_data.get("jti")
        if jti:
            revoked_jti.add(jti)
    except Exception:
        pass

    resp = redirect(url_for("login"))
    unset_jwt_cookies(resp)
    flash("성공적으로 로그아웃되었습니다.", "info")
    return resp


if __name__ == "__main__":
    app.run(debug=True)
