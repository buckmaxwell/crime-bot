from sqlalchemy import Column, Integer, String, Float
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from flask import Flask, jsonify, request


class CN_StolenProperty(Base):
	__tablename__	= 'cn_stolen_property'

	id 				= Column(Integer, primary_key=True)
	code 			= Column(Integer, ForeignKey('property_types.code'))
	manufacturer	= Column(String)
	model			= Column(String)
	description		= Column(String)
	value			= Column(Float)
	reportID		= Column(Integer, ForeignKey('cn_reports.id'))

	report = relationship("CN_Report", backref=backref('cn_stolen_property'))
	property_type = relationship("PropertyType", backref=backref('cn_stolen_property'))


def add_property(session, json):
	token		= json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})
	report_id 	= json.get('id',None)
	if not report_id:
		return jsonify({'ERROR':'no report id given'})
	for p in json["property"]:
		try:
			_code			= p['code']
			_manufacturer 	= p.get('manufacturer', None)
			_model			= p.get('model', None)
			_description	= p['description']
			_value			= p['value']
		except:
			return jsonify({'ERROR':'critical offense information missing'})
		prop = CN_StolenProperty(code=_code, manufacturer=_manufacturer, model=_model, \
			description=_description, value=_value, reportID=report_id)
		session.add(prop)
		try:
			session.commit()
		except:
			session.rollback()
	return jsonify({'result':'true'})


def make_property(session, json):
	propert = json.get('property', None)
	if not propert:
		return True
	token		= json.get('token', None)
	if not token:
		return False
	report_id 	= json.get('id',None)
	if not report_id:
		return False
	for p in json["property"]:
		try:
			_code			= p['code']
			_manufacturer 	= p.get('manufacturer', None)
			_model			= p.get('model', None)
			_description	= p['description']
			_value			= p['value']
		except:
			return False
		prop = CN_StolenProperty(code=_code, manufacturer=_manufacturer, model=_model, \
			description=_description, value=_value, reportID=report_id)
		session.add(prop)
		try:
			session.commit()
		except:
			session.rollback()
	return True