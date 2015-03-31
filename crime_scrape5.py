import requests
from bs4 import BeautifulSoup as bs
from address import AddressParser, Address
import re
import time
#db
#uncomment to create tables
import db_create

import db
from db import Base
#own packages
import subject
import officer
import offenses
import people_businesses
import property
import case
#
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import update

import sys, os
from sqlalchemy import desc


def make_case(session,caseID):
	if session.query(case.Case).filter(case.Case.id==caseID).all():
		return False
	url = 'http://www.columbuspolice.org/reports/PublicReport?caseID=' + str(caseID)
	original = requests.get(url)
	page = bs(original.text)
	#if "failed" in page.find_all(id='view1')[0].find_all('td')[1].text:
		#print "that was a bad caseID"
		#return False
	m = page.find_all(id='view1')
	mPrefix = m[0].find_all('td')
	if not mPrefix[5].text.strip():
		return False #if there is no report number there is no case
	#add case
	current_case = case.Case(id=caseID)
	session.add(current_case)
	session.commit()
	#prepare address
	location = mPrefix[9].text.strip()
	ap = AddressParser()
	address = ap.parse_address(location)
	#prepare officer
	officer_name= mPrefix[27].text.strip()
	officer_badge = mPrefix[29].text.strip().strip()
	#prepare offenses
	o = page.find_all(id='view2')
	oPrefix = o[0].find_all('td')
	#prepare property
	p = page.find_all(id='view5')
	pPrefix = p[0].find_all('td')
	#prepare apartment
	numbers = re.compile('\d+(?:\.\d+)?')
	#case
	_id = caseID
	_number = mPrefix[1].text.strip()
	_title = mPrefix[3].text.strip()
	_report_no = mPrefix[5].text.strip()
	_subjectcode = subject.make_subject(session, mPrefix[7].text.strip(), _title)
	try:
		_house_number = int(address.house_number)
	except:
		_house_number = None
	_street_prefix = address.street_prefix
	_street = address.street
	_street_suffix = address.street_suffix
	try:
		_apartment = int(numbers.findall(address.apartment)[0])
	except:
		_apartment = None
	_city = mPrefix[11].text.strip()
	try:
		_zone = int(mPrefix[13].text.strip())
	except:
		_zone = None
	try:
		_precinct = int(mPrefix[15].text.strip())
	except:
		_precinct = None
	try:
		_district = int(mPrefix[17].text.strip())
	except:
		_district = None
	_crime_began = mPrefix[19].text.strip()
	_crime_ended = mPrefix[21].text.strip()
	_report_date = mPrefix[23].text.strip()
	#replace N/A with None type for dates
	if len(_crime_began) < 4:
		_crime_began = None
	if len(_crime_ended) < 4:
		_crime_ended = None
	if len(_report_date) < 4:
		_report_date = None
	_badge = officer.make_officer(session, officer_name, officer_badge)
	_description = mPrefix[30].text.strip()
	offenses.make_offenses(session, caseID, oPrefix)
	people_businesses.make_victim_or_arrestee(_report_date, session, caseID, page)
	people_businesses.make_victim_or_arrestee(_report_date, session, caseID, page, False)
	property.make_stolen_properties(session, pPrefix, caseID)
	#end case bvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	conn = db.get_engine().connect()
	stmt = case.Case.__table__.update().\
	values(number=_number, title=_title, report_no=_report_no, \
		subjectcode=_subjectcode, house_number=_house_number, \
		street_prefix=_street_prefix, street=_street, street_suffix=_street_suffix, \
		apartment=_apartment, city=_city, zone=_zone, precinct=_precinct, \
		district=_district, crime_began=_crime_began, crime_ended=_crime_ended, \
		report_date=_report_date, badge=_badge, description=_description).\
	where(case.Case.id == caseID)
	conn.execute(stmt)
	conn.close()
	session.add(current_case)
	session.commit()
	return True  
	

#from 4022000 to 4099410
#PROG FAILED, starting again from 4024569, 4027140-40245694027140-4024569
#to start
#nohup python *5.py > log.txt 2>&1 &
def start():
	session = db.setup_session()
	#session.query(Cases)
	results = session.query(case.Case).order_by(desc(case.Case.id)).limit(1).all()
	try:
		caseID = results[0].id
	except:
		caseID = 4022000
	stop = caseID + 400
	#caseID = 4022000
	#caseID = 4024569
	#caseID = 4030330
	#END NUMBER = 4190000
	while caseID < stop:
		try:
			print make_case(session, caseID)
			print "SUCCESS ON"
			print caseID	
		except Exception as e:
			print "FAILED ON"
			print caseID
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			print e
		time.sleep(0.5)
		caseID+=1
	session.close()

#MAIN
start()


#TESTS
'''
print "TRYING, caseID 4022000 -- already in db"
print make_case(4022000)
print "TRYING, caseID 4022007 -- has arestee"
print make_case(4022007)
print "TRYING, caseID 4030094 -- business/no arestee"
print make_case(4030094)
print "TRYING, caseID 4022090 -- multiple offenses/non-uniform title/badge 0"
print make_case(4022090)
'''

