from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_TABLE_NAME, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

Base = declarative_base()


class ConsumerConfig(Base):
    __tablename__ = DB_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    consumer_name = Column(String, unique=True, nullable=False)
    topics_input = Column(String, nullable=False)
    topics_output = Column(String, nullable=False)
    metadatas = Column(String, nullable=True)  # Optional metadata field
    kafka_bootstrap_server = Column(String, nullable=False)
    timeout = Column(Integer, nullable=True)  # Optional timeout field


def get_engine():
    return create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')


def create_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
