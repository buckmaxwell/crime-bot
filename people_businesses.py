from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from bs4 import BeautifulSoup as bs
from nameparser import HumanName
from address import AddressParser, Address
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
#mine
import db
from db import Base
#
#age manip
import timestring
#
from fuzzywuzzy import fuzz

#TODO: change vars for make_person and get rid of all the damn V's


class Person(Base):
	__tablename__='people'

	id = Column(Integer, primary_key=True)
	fname = Column(String)
	lname = Column(String)
	mname = Column(String)
	name_suffix = Column(String)
	name_title = Column(String)
	sex = Column(String)
	race = Column(String)
	dob_est = Column(DateTime)
	house_number = Column(String)
	street_prefix = Column(String)
	street = Column(String)
	street_suffix = Column(String)
	apartment = Column(String)
	zip = Column(String)
	victim = Column(Boolean)
	arrestee = Column(Boolean)

class Business(Base):
	__tablename__='businesses'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	house_number = Column(String)
	street_prefix = Column(String)
	street = Column(String)
	street_suffix = Column(String)
	apartment = Column(String)
	zip = Column(String)

class Case_Person(Base):
	__tablename__ = 'case_person'

	case = Column(Integer, ForeignKey('cases.id'), primary_key=True )
	person = Column(Integer, ForeignKey('people.id'), primary_key=True)
	is_victim = Column(Boolean)



class Case_Business(Base):
	__tablename__ = 'case_business'

	case = Column(Integer, primary_key=True)
	business = Column(Integer, primary_key=True)


def get_estimated_dob(d, age):
	d.year -= age
	if d.day > 28:
		d.day = 28
	if d.month < 6:
		d.year -=1
		d.month = 12 - (6-d.month)
	else:
		d.month -= 6
	return d

def check_age_in_range(_d1,_d2):
	d1 = _d1
	d2 = _d2
	if d1 == d2: #if dates are exactly equal return true.
		return True
	if d1 > d2: #if d1 is greater add 2 to d2 and check which is greater
		d2.year+=2
		return d2 > d1
	else:
		d1.year+=2
		return d1 > d2#1985-06-28 01:09:12, 1986-04-15 02:05:00

def potential_person(session, _case, _fname, _lname, _dob_est, _street, _house_number, _sex, _race):
	results = session.query(Person).filter(func.lower(Person.lname) == func.lower(_lname))\
	.filter(func.lower(Person.sex) == func.lower(_sex))\
	.filter(func.lower(Person.race) == func.lower(_race)).all()
	#to be a match person must have at least the same last name, sex, and race
	bday = timestring.Date(_dob_est)
	result = False
	for p in results:
		p_bday = timestring.Date(p.dob_est)
		try:
			name_ratio = fuzz.ratio(p.fname.lower(), _fname.lower() )
		except:
			name_ratio = 0
		try:
			street_ratio = fuzz.ratio(p.street.lower(), _street.lower())
		except:
			street_ratio = 0
		try:
			house_ratio = fuzz.ratio(p.house_number.lower(), _house_number.lower())
		except:
			house_ratio = 0
		age_range = check_age_in_range(bday,p_bday)
		if name_ratio > 85 and age_range:
			result = p
		elif name_ratio > 75 and age_range and street_ratio > 95 and house_ratio > 95:
			result = p
	if result:
		#BELOW: protection against victim twins in the same case
		x = session.query(Case_Person).filter(Case_Person.case == _case).filter(Case_Person.person == result.id).all()
		if x:
			result = False
		if _fname.lower() == "juvenile":
			result = False
	return result

	
#shouldn't this check street?
def potential_business(session, _name, _street, _house_number):
	results = session.query(Business).filter(func.lower(Business.street) == func.lower(_street)).all()
	result = False
	for b in results:
		try:
			name_ratio = fuzz.ratio(b.name.lower(), _name.lower())
		except:
			name_ratio = 0
		try:
			house_ratio = fuzz.ratio(b.house_number.lower(), _house_number.lower())
		except:
			house_ratio = 0
		if name_ratio > 95 and house_ratio > 75:
			result =  b
		elif name_ratio > 85 and house_ratio > 99:
			result =  b
	return result


def make_person(report_date, session, i, _case, vPrefix, _is_victim):
	vName = vPrefix[i+4].text.strip()				#name of victim 1
	parsed_name = HumanName(vName)
	vSexRaceAge = vPrefix[i+5].text.strip() 			#sex/race/age
	vAddressLine1 = vPrefix[i+8].text.strip()	#victim address line 1
	vAddressLine2 = vPrefix[i+9].text.strip()	#victim address line 2
	ap = AddressParser()
	vAddr1 = ap.parse_address(vAddressLine1)
	vAddr2 = ap.parse_address(vAddressLine2)
	vSRA_array = vSexRaceAge.split(' / ')
	_fname = parsed_name.first
	_lname = parsed_name.last
	_mname = parsed_name.middle
	_name_suffix = parsed_name.suffix
	_name_title = parsed_name.title
	_sex = vSRA_array[0]
	_race = vSRA_array[1]
	_age = vSRA_array[2]
	try:
		d = timestring.Date(report_date)
		a = int(_age)
		_dob_est = str(get_estimated_dob(d, a))
	except:
		_dob_est = None
	_house_number = vAddr1.house_number
	_street_prefix = vAddr1.street_prefix
	_street = vAddr1.street
	_street_suffix = vAddr1.street_suffix
	_apartment= vAddr1.apartment
	_zip = vAddr2.zip
	# TODO Need to add better checker BELOW
	person_exists = potential_person(session, _case, _fname, _lname, _dob_est, _street, _house_number, _sex, _race)
	if not person_exists:
		person = Person(fname=_fname, lname=_lname, mname=_mname, name_suffix=_name_suffix, \
			name_title=_name_title, sex=_sex, race=_race, dob_est=_dob_est, house_number=_house_number, \
			street_prefix=_street_prefix, street=_street, street_suffix=_street_suffix, \
			apartment=_apartment, zip=_zip)
		session.add(person)
		session.commit()
		id = person.id
	else:
		id = person_exists.id
	cp = Case_Person(case=_case, person=id, is_victim=_is_victim)
	session.add(cp)
	session.commit()
	return True


def make_business(session, i, _case, vPrefix):
	vAddressLine1 = vPrefix[i+8].text.strip()	#victim address line 1
	vAddressLine2 = vPrefix[i+9].text.strip()	#victim address line 2
	ap = AddressParser()
	vAddr1 = ap.parse_address(vAddressLine1)
	vAddr2 = ap.parse_address(vAddressLine2)
	_name = vPrefix[i+4].text.strip()				#name of victim 1
	_house_number = vAddr1.house_number
	_street_prefix = vAddr1.street_prefix
	_street = vAddr1.street
	_street_suffix = vAddr1.street_suffix
	_apartment= vAddr1.apartment
	_zip = vAddr2.zip
	business_exists = potential_business(session, _name, _street, _house_number)
	if business_exists:
		id = business_exists.id
		session.commit()
	else:
		victim = Business(name=_name, \
			house_number=_house_number, \
			street_prefix=_street_prefix, street=_street, street_suffix=_street_suffix, \
			apartment=_apartment, zip=_zip )
		session.add(victim)
		session.commit()
		id = victim.id
	cb = Case_Business(case=_case, business=id)
	session.add(cb)
	session.commit()
	return id



def make_victim_or_arrestee(report_date, session, _caseID, page, is_victim=True):
	i = 0
	people = []
	businesses = []
	try:
		if is_victim:
			v = page.find_all(id='view3')
			vPrefix = v[0].find_all('td')
			leng = len(vPrefix)
			while i < leng:
				try:
					if "[E]" in vPrefix[i+4].text.strip():
						businesses.append(make_business(session, i, _caseID, vPrefix))
					else:
						people.append(make_person(report_date, session, i, _caseID, vPrefix, is_victim))
				except Exception as e:
					pass
				i+=11
		else:
			a = page.find_all(id='view4')
			aPrefix = a[0].find_all('td')
			leng = len(aPrefix)
			while i < leng:
				try:
					people.append(make_person(report_date, session, i, _caseID, aPrefix, is_victim))
				except Exception as e:
					pass
				i+=11
	except Exception as e:
		pass
	return (people, businesses)