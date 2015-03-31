from sqlalchemy import Column, Integer, String, Numeric, DateTime
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from flask import Flask, jsonify, request
import timestring
import cn_reports

class CN_Perpetrator(Base):
	__tablename__ 	= 'cn_perpetrators'

	id 				= Column(Integer, primary_key=True)
	est_dob			= Column(DateTime)
	sex				= Column(String)
	race			= Column(String)
	description		= Column(String)
	reportID		= Column(Integer, ForeignKey('cn_reports.id'))

	report 			= relationship("CN_Report", backref=backref('cn_perpetrators'))


def get_estimated_dob(d, age):
	print d
	print d.year
	d.year -= age
	if d.day > 28:
		d.day = 28
	if d.month < 6:
		d.year -=1
		d.month = 12 - (6-d.month)
	else:
		d.month -= 6
	return str(d)


def add_perpetrators(session, json):
	token	 		= json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})
	report_id 		= json.get('id',None)
	if not report_id:
		return jsonify({'ERROR':'no report id given'})
	for perp in json['perpetrators']:
		try:
			_est_dob 	 = get_estimated_dob(timestring.now(), int(perp['age']))
			_sex 		 = perp['sex']
			_race 		 = perp['race']
			_description = perp['description']
		except Exception as e:
			print e
			return jsonify({'ERROR':'missing information for perpetrator'})
		p = CN_Perpetrator(est_dob=_est_dob, sex=_sex, race=_race, description=_description,\
			reportID=report_id)
		session.add(p)
		try:
			session.commit()
			cn_reports.calculate_score(session, report_id)
		except Exception as e:
			session.rollback()
			return jsonify({'ERROR':str(e)})
	return jsonify({'result':'true'})


def make_perpetrators(session, json):
	print json
	perpetrators = json.get('perpetrators', None)
	print perpetrators
	if not perpetrators:
		return True
	token	 		= json.get('token', None)
	if not token:
		return False
	report_id 		= json.get('id',None)
	if not report_id:
		return False
	for perp in json['perpetrators']:
		try:
			_est_dob 	 = get_estimated_dob(timestring.now(), int(perp['age']))
			_sex 		 = perp['sex']
			_race 		 = perp['race']
			_description = perp['description']
		except Exception as e:
			print e
			return False
		p = CN_Perpetrator(est_dob=_est_dob, sex=_sex, race=_race, description=_description,\
			reportID=report_id)
		session.add(p)
		try:
			session.commit()
			cn_reports.calculate_score(session, report_id)
		except Exception as e:
			print str(e)
			session.rollback()
			return False
	return True