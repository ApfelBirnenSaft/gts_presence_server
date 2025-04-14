from sqlmodel import SQLModel, create_engine, Session

engine = create_engine(f"mysql+pymysql://root:iz*&3rmz&*!wL7%40s@192.168.2.102:3307/gtsv2?charset=utf8mb4", echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
