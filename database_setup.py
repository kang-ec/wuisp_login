import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect('vuln_database.db')
cursor = conn.cursor()

# users 테이블 생성 (만약 이미 존재하면 삭제 후 다시 생성)
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);
""")

# 테스트용 데이터 추가
# 비밀번호 'test'를 평문으로 저장
cursor.execute("INSERT INTO users (user_id, password, email) VALUES (?, ?, ?)", 
               ('testuser', 'test', 'test@example.com'))


conn.commit()
conn.close()

print("취약점 실습용 데이터베이스(vuln_database.db) 생성이 완료되었습니다.")
print("'testuser' / 'test' 계정이 추가되었습니다.")