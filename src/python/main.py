from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, Session

# Настройки подключения к базе данных
DATABASE_URL = "postgresql://user:password@localhost/mydatabase"

# Настройка SQLAlchemy
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(bind=engine))

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)

class TextFile(Base):
    __tablename__ = 'text_files'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)

app = FastAPI()

# Создание таблиц при старте приложения
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

# Генератор сессий для работы с базой данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.remove()  # Освобождаем сессию

# Эндпоинт для загрузки файла
@app.post("/upload")
async def upload_file(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    new_file = TextFile(user_id=user_id, content=content.decode('utf-8'))
    db.add(new_file)
    db.commit()
    return {"message": "File uploaded successfully!"}
