from sqlalchemy import Column, Integer, String
from nameparser import HumanName
#mine
import db
from db import Base


class Officer(Base):
	__tablename__='officers'

	badge = Column(Integer, primary_key=True)
	title = Column(String)
	last_name = Column(String)

def make_officer(session, _name, _badge):
	parsed_name = HumanName(_name)
	_title = parsed_name.title
	_last_name = parsed_name.last
	_badge = int(_badge)
	if _badge != 0 and not session.query(Officer).filter(Officer.badge == _badge).all():
		officer = Officer(badge=_badge, title=_title, last_name=_last_name)
		session.add(officer)
		session.commit()
	elif _badge == 0 and not session.query(Officer).filter(Officer.badge == _badge).all():
		officer = Officer(badge=_badge, title="ReportFiler", last_name="NonOfficer")
		session.add(officer)
		session.commit()
	return _badge