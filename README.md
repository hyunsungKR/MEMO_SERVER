# 로그인과 로그아웃이 가능한 메모장 Restful API 서버 개발 👀

## 📌 기능 설명

* 로그인, 로그아웃 기능
* Visual Studio Code에서 flask 프레임워크로 작업
* 유지보수작업을 수월하게 하기 위해서 다른 파일에서 클래스를 만들고 그 함수를 import해서
* 메모 작성, 수정, 삭제 기능
* 자신의 메모 보기 기능, 다른 사람은 열람 불가
* 팔로우한 친구의 메모 공유
* Config.py 파일에 host와 DB_PASWORD와 같은 해킹에 위험한 문자열은 클래스 안에 변수로 저장

## 📌DB구조 (MySQL Workbench)


### Table : user
- Columns
  - id : 기본 인덱스 (INT/ PK, NN, UN, AI)
  - email : 이메일 (VARCHAR(45)/ UQ)
  - password : 비밀번호 (VARCHAR256)
  - nickname : 사용자 이름 (VARCHAR45)
  - createdAt : 생성일자 (TIMESTAMP) / Default=now()
### Table : memo
- Columns
  - id : 기본 인덱스 (INT/ PK, NN, UN, AI)
  - title : 메모의 제목 (VARCHAR(45)
  - date : 이행 시간 (VARCHAR(45)
  - content : 메모 내용 (VARCHAR(256)
  - createdAt : 메모 생성일 (TIMESTAMP)/ Default=now()
  - updatedAt : 메모 수정일 (TIMESTAMP)/ Default=now() on update now()
  - userId : Foreign Key Value (INT/ NN, UN)
- Foreign Keys
  - memo table : user_id -> user table : id
  
### Table : follow
- Columns
    - followerId : 팔로우한 user.id (INT/ UN)
    - followeeId : 팔로우 당한 user.id (INT/ UN)
    - createdAt : 팔로우한 날짜와 시간 (TIMESTAMP)/ Default=now()
- Foreign Keys
  - follow table : followerId -> user table : id
  - follow table : followeeId -> user table : id
- Indexes
  - Type : UNIQUE
  - Column : followerId, followeeId
  
## 📌각 파일 설명
**app.py**
- API의 기본 틀이 되는 메인 파일
- 가상 환경 셋팅
- JWT 토큰을 생성과 파괴
- 리소스화 된 클래스들의 경로 설정 (API 기능)

---

**mysql_connection.py**
- DB 연동에 관련된 함수를 정의한 파일
``` python
import mysql.connector

from config import Config

def get_connection() :
    connection = mysql.connector.connect(host= Config.HOST,
    database = Config.DATABASE,
    user = Config.DB_USER,
    password = Config.DB_PASSWORD
    )
    return connection
```

---

**config.py**
- 가상 환경의 값을 설정하는 파일
  - 토큰의 암호화 방식 설정
    - 토큰의 시크릿 키와 DB의 모든 정보는 비공개
**utils.py**
- 사용자로부터 입력받은 비밀번호를 암호화하는 파일
  - 입력 받은 비밀번호를 해시로 매핑하여 암호화
  - 암호화된 비밀번호와 새로 입력 받은 값이 같은지 확인
```python
from passlib.hash import pbkdf2_sha256

from config import Config

# 원문 비밀번호를, 암호화 하는 함수

def hash_password(original_password) :

    password=original_password + Config.SALT
    password=pbkdf2_sha256.hash(password)
    return password

# 유저가 로그인할 때 입력한 비밀번호가 맞는지 체크하는 함수
def check_password(original_password,hashed_password) :

    password=original_password + Config.SALT
    check = pbkdf2_sha256.verify(password,hashed_password)
    return check
 ```

---

**user.py**
- Class UserRegisterResource
  - 회원가입을 하면 DB에 입력한 정보가 등록되는 기능
    - 이메일과 비밀번호 유효성 검사
    - 비밀번호 암호화, 식별 ID 토큰화
- class UserLoginResource
  - 로그인
    - DB에 입력한 이메일 존재 유무와 비밀번호 동일 유무 확인
    - 입력한 데이터가 DB의 정보와 일치하면 식별 ID 토큰 생성
- class UserLogoutResource
  - 로그아웃
    - 생성된 토큰을 파괴  

---

 **memo.py**
- class MemoResource
  - 입력한 메모를 작성
  - 작성한 메모 조회
    - 다른 사람의 메모는 조회 불가
  - 작성한 메모 수정
    - 친구의 메모는 조회만 가능하며, 수정은 불가
  - 작성한 메모 삭제
    - 삭제 또한 친구의 메모는 삭제 불가
 ```python
  # 페이징처리 ( query string )
         offset = request.args.get('offset')
        limit=request.args.get('limit')


        try :
            connection = get_connection()

            query = '''select *
                        from memo
                        order by date desc
                        limit '''+ offset +''','''+ limit +''';'''
 ```

**follow.py**
- class Friends
    - 팔로우
      - 이메일 존재 유무 확인
      - 이메일이 존재하면 팔로우
    - 팔로우한 친구의 메모 함께 보기
      - 팔로우한 친구(followee)의 메모와 내 메모를 함께 리스트로 출력
    - 팔로우 해제
      - 팔로우 테이블의 데이터를 삭제
      - 팔로우를 해제하면 상대와 나의 메모가 보이지 않음
