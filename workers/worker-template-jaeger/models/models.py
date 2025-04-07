from distutils.command.config import config

from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

Base = declarative_base()


class ConsumerConfig(Base):
    __tablename__ = Config.DB_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    consumer_name = Column(String(255), unique=True, nullable=False)
    topics_input = Column(String(255), nullable=False)
    topics_output = Column(String(255), nullable=False)
    metadatas = Column(String(8192), nullable=True)
    kafka_bootstrap_server = Column(String(255), nullable=False)
    timeout = Column(Integer, nullable=True)


def get_engine():
    return create_engine(f'mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}')


def create_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)

