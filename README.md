# Flask Login & JWT Practice
Flask 기반 로그인 시스템 실습 프로젝트입니다.  
로그인 페이지 취약점 실습 버전과 JWT 인증 적용/보안 강화 버전을 브랜치로 분리하여 관리합니다.

---

## 프로젝트 소개
 프로젝트는 정보보호 전공 실습의 일환으로,  
기본 로그인 인증 구조와 JWT(JSON Web Token) 기반 인증 방식을 단계적으로 학습하기 위해 제작되었습니다.  
JWT 적용 전/후 구조 및 보안 강화 요소를 비교하는 것을 목표로 합니다.

---

## Branch 설명

### `main` — 로그인 페이지 취약점 실습 ver
- JWT 적용 전 기본 로그인 구조
- 세션 기반 인증 방식
- 로그인 페이지 취약점 학습용 베이스라인

### `jwt-basic` — JWT 적용 ver
- 로그인 성공 시 JWT Access Token 발급
- `@jwt_required()`를 이용한 보호 API 구성
- JWT 동작 원리 학습 목적

### `jwt-secure` — JWT 보안 강화 ver
- JWT를 HttpOnly 쿠키로 저장
- Access / Refresh Token 분리
- 로그아웃 시 토큰 무효화 구조
- 보안 요소를 고려한 JWT 인증 구조

---

## 실행 방법

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py

---

# 프로젝트 구조
.
├── app.py
├── templates/
│   ├── login.html
│   ├── signup.html
│   └── welcome.html
└── venv/
