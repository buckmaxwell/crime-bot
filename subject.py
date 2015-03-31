from sqlalchemy import Column, Integer, String
#mine
import db
from db import Base

class Subject(Base):
	__tablename__ = 'subjects'
	
	code = Column(String, primary_key=True)
	description = Column(String)


def make_subject(session, subject, title):
	mSC_array= subject.strip().split(' - ', 1)
	try:
		_code = mSC_array[0]
		_description = mSC_array[1]
	except:
		mSC_array= title.strip().split(' - ', 1)
		_code = mSC_array[0]
		_description = mSC_array[1]
	if not session.query(Subject).filter(Subject.code == _code).all():
		subject = Subject(code=_code, description=_description)
		session.add(subject)
		session.commit()
	return _code
