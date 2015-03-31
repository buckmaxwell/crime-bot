from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#
from sqlalchemy.pool import NullPool
#
Base = declarative_base()
import atexit

def get_engine():
	url = 'postgresql://%s:%s@localhost:5432/crimedb' % ('crimeapp', 'wearethesuperhero500lovemax')
	return create_engine(url, poolclass=NullPool)

def setup_session():
    db = get_engine()
    session = sessionmaker(bind=db)
    db_session = session()
    atexit.register(db_session.close)
    return db_session
