from sqlalchemy import Column, Integer, String, Numeric
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
import re

class Offense(Base):
	__tablename__='offenses'

	lcode = Column(Numeric, primary_key=True)
	lcode_ext = Column(String, primary_key=True)
	description = Column(String)
	completed = Column(String)#maybe should be bool or char

class OhioRevisedCode(Base):
	__tablename__='ohio_revised_codes'

	code = Column(Numeric, primary_key=True)
	link = Column(String)

class Case_Offense(Base):
	__tablename__ = 'case_offense'

	case = Column(Integer, primary_key=True)
	lcode = Column(Numeric, primary_key=True)
	lcode_ext = Column(String, primary_key=True)


def make_offense(session, _caseID, oDescrip, oCompleted):
	oDescripArray = oDescrip.split(' - ', 1)
	oLongCodeArray = oDescripArray[0].split('.')
	try:
		_lcode = int(oLongCodeArray[0])/100.00
	except:
		numbers = re.compile('\d+(?:\.\d+)?')
		_lcode = int(numbers.findall(oLongCodeArray[0])[0])/100.00
	_lcode_ext = oLongCodeArray[1]
	_description = oDescripArray[1]
	_completed = oCompleted
	if not session.query(Offense).filter(Offense.lcode == _lcode).filter(Offense.lcode_ext == _lcode_ext).all():
		offense = Offense(lcode=_lcode, lcode_ext=_lcode_ext, description=_description, \
			completed=_completed)
		session.add(offense)
	if not session.query(OhioRevisedCode).filter(OhioRevisedCode.code == _lcode).all():
		_lcode_link = 'http://codes.ohio.gov/orc/' + str(_lcode)
		orc = OhioRevisedCode(code=_lcode, link=_lcode_link)
		session.add(orc)
	if not session.query(Case_Offense).filter(Case_Offense.case == _caseID)\
	.filter(Case_Offense.lcode == _lcode).filter(Case_Offense.lcode_ext == _lcode_ext).all():
		co = Case_Offense(case=_caseID, lcode=_lcode, lcode_ext=_lcode_ext)
		session.add(co)
	return _lcode

	
def make_offenses(session, _caseID, oPrefix):
	offenses = True
	try:
		leng = len(oPrefix)
		i = 0
		while i < leng:
			oDescrip = oPrefix[i + 4].text.strip()
			oCompleted = oPrefix[i+6].text.strip()
			oOffense = make_offense(session, _caseID, oDescrip, oCompleted)
			i+=8
	except Exception as e:
		print e
		offenses = False
	session.commit()
	return True

