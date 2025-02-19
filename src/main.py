from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import List, Optional

app = FastAPI()

# SQLite 데이터베이스 설정
DATABASE_URL = "sqlite:///./diary.db"
TEST_DATABASE_URL = "sqlite:///./test_diary.db"
engine = create_engine(DATABASE_URL, echo=True)
test_engine = create_engine(TEST_DATABASE_URL, echo=True)

# when test ends, drop all tables
def drop_all_tables():
    SQLModel.metadata.drop_all(engine)

# --- 모델 정의 ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password_hash: str
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""

class DiaryEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    entry_date: Optional[str] = None
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""
    


class DiaryLine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    diary_id: int
    line_order: int
    language: str  # "ko" 또는 "en"
    content: str
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""

# 데이터베이스 테이블 생성
# def create_db_and_tables():
SQLModel.metadata.create_all(engine)

# 세션 종속성
def get_session():
    with Session(engine) as session:
        yield session

# --- API 엔드포인트 ---
# create authentication api code here


# ✅ 0. 전체 사용자 조회
@app.get("/users/")
def read_users(session: Session = Depends(get_session)):
    statement = select(User)
    users = session.exec(statement).all()
    return users

# ✅ 0. 사용자 조회 (특정 사용자)
@app.get("/users/{user_id}/")
def read_user(user_id: int, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없음.")
    return user

# 0. 사용자 조회 by email
@app.get("/users/{email}/")
def read_user(email: str, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없음.")
    return user


# ✅ 1. 사용자 등록
@app.post("/users/")
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# ✅ 2. 새 일기 생성
@app.post("/diary/")
def create_diary_entry(user_id: int, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없음.")

    diary_entry = DiaryEntry(user_id=user_id)
    session.add(diary_entry)
    session.commit()
    session.refresh(diary_entry)
    return diary_entry

# ✅ 3. 일기 한 줄 추가
@app.post("/diary/{diary_id}/lines/")
def add_diary_line(diary_id: int, line_order: int, language: str, content: str, session: Session = Depends(get_session)):
    diary_line = DiaryLine(diary_id=diary_id, line_order=line_order, language=language, content=content)
    session.add(diary_line)
    session.commit()
    session.refresh(diary_line)
    return diary_line

# ✅ 4. 특정 일기의 전체 내용 조회
@app.get("/diary/{diary_id}/")
def get_diary_lines(diary_id: int, session: Session = Depends(get_session)):
    statement = select(DiaryLine).where(DiaryLine.diary_id == diary_id).order_by(DiaryLine.line_order, DiaryLine.language)
    results = session.exec(statement).all()
    return results

# ✅ 5. 특정 라인 수정 (NEW 기능 추가)
@app.put("/diary/{diary_id}/lines/{line_id}/")
def update_diary_line(diary_id: int, line_id: int, new_content: str, session: Session = Depends(get_session)):
    # 수정할 라인 찾기
    statement = select(DiaryLine).where(DiaryLine.id == line_id, DiaryLine.diary_id == diary_id)
    diary_line = session.exec(statement).first()

    # 라인이 존재하지 않는 경우 예외 발생
    if not diary_line:
        raise HTTPException(status_code=404, detail="해당 라인을 찾을 수 없음.")

    # 내용(content)만 수정
    diary_line.content = new_content
    session.add(diary_line)
    session.commit()
    session.refresh(diary_line)

    return diary_line

