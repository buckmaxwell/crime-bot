from sqlalchemy import Column, Integer, Numeric
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from flask import Flask, jsonify, request


class CN_Report_OhioRevisedCode(Base):
	__tablename__		= 'cn_report_ohio_revised_code'

	report 				= Column(Integer, ForeignKey('cn_reports.id'), primary_key=True)
	ohio_revised_code 	= Column(Numeric, ForeignKey('ohio_revised_codes.code'), primary_key=True)

	orc = relationship("OhioRevisedCode", backref=backref('cn_report_ohio_revised_code'))
	rep = relationship("CN_Report", backref=backref('cn_report_ohio_revised_code'))


def add_offenses(session, json):
	token		= json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})
	report_id 	= json.get('id',None)
	if not report_id:
		return jsonify({'ERROR':'no report id given'})
	for o in json['offenses']:
		try:
			_orc= o['ohio_revised_code']
		except:
			return jsonify({'ERROR':'critical offense information missing'})
		offense = CN_Report_OhioRevisedCode(report=report_id, ohio_revised_code=_orc)
		session.add(offense)
		try:
			session.commit()
		except:
			session.rollback()
	return jsonify({'result':'true'})


def make_offenses(session, json):
	offenses = json.get('offenses', None)
	if not offenses:
		return True
	token		= json.get('token', None)
	if not token:
		return False
	report_id 	= json.get('id',None)
	if not report_id:
		return False
	for o in json['offenses']:
		try:
			_orc= o['ohio_revised_code']
		except:
			return False
		offense = CN_Report_OhioRevisedCode(report=report_id, ohio_revised_code=_orc)
		session.add(offense)
		try:
			session.commit()
		except:
			session.rollback()
	return True