from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean
from address import AddressParser, Address
#mine
import db
from db import Base
import cn_users
import cn_perpetrators
import cn_report_orc
import cn_property
import cn_comments

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from flask import Flask, jsonify, request
import timestring
import json
from urllib2 import Request, urlopen, URLError
#1d44bb7d-f8d7-4326-aae3-3acc0e4e1835
'''
curl -i -H "Content-Type: application/json -X GET -d '{"token":"1d44bb7d-f8d7-4326-aae3-3acc0e4e1835", "title":"test title", "subjectcode":"115", "address_line1":"7001 W Clinton Ave", "lat_reported_from":"41.4819780", "lon_reported_from":"-81.7330550", "time_reported":"03-15-2015 10:34 PM", "description":"This never happened.  This is a test report"}' http://jeffcasavant.com:10122/reports/new
'''
class CN_Report(Base):
	__tablename__ 		= 'cn_reports'

	id 			 		= Column(Integer, primary_key=True)
	title				= Column(String)
	subjectcode			= Column(String, ForeignKey('subjects.code'))
	house_number		= Column(String)
	street_prefix		= Column(String)
	street 				= Column(String)
	street_suffix		= Column(String)
	apartment			= Column(String)
	lon 				= Column(Numeric)
	lat 				= Column(Numeric)
	lon_reported_from	= Column(Numeric)
	lat_reported_from	= Column(Numeric)
	time_reported		= Column(DateTime)
	time_began			= Column(DateTime)
	time_ended			= Column(DateTime)
	is_emergency		= Column(Boolean)
	description			= Column(String)
	user_id				= Column(Integer, ForeignKey('cn_users.id'))
	spam_count			= Column(Integer)
	score				= Column(Integer)

	subject 			= relationship("Subject", backref=backref('cn_reports'))
	user 				= relationship("CN_User", backref=backref('cn_reports'))


def get_lonlat(location):
	API_KEY = "AIzaSyAgw7ZFrTPcUB3okQqv8Ii2fNu_7091a_M"
	location = location.replace (" ", "+")
	"""Example location: 1600+Amphitheatre+Parkway,+Mountain+View,+CA"""
	lonlat = []
	reqStr = "https://maps.googleapis.com/maps/api/geocode/json?address="+location+"key="+API_KEY
	try:
		request = Request(reqStr)
		response = urlopen(request)
		location_json = json.loads(response.read())
		if len(location_json["results"])!=0:
			lon = location_json["results"][0]["geometry"]["location"]["lng"]
       			lat = location_json["results"][0]["geometry"]["location"]["lat"]
       			lonlat.append(lon)
       			lonlat.append(lat)
	except URLError, e:
		print "get_lonlat(location):",e
	return lonlat


def calculate_score(session, reportid):
	score  = 25 
	report = session.query(CN_Report).filter(CN_Report.id == reportid).all()[0]
	perps  = session.query(cn_perpetrators.CN_Perpetrator)\
	.filter(cn_perpetrators.CN_Perpetrator.reportID == reportid).count()
	commen = session.query(cn_comments.CN_Comments)\
	.filter(cn_comments.CN_Comments.reportID == reportid).count()
	if report.is_emergency: 
		score+=10
	for commentnum in range(1, commen+1):
		score+=25/commentnum
	for perpnum in range(1, perps+1):
		score+=5/perpnum
	score-=report.spam_count*2
	report.score = score
	session.commit()


def make_report(session, json):
	token	 				= json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})

	if not cn_users.get_userid(session, token):
		return jsonify({'ERROR':'bad token'})

	try:
		_title 				= json.get('title', None)
		_subjectcode		= json['subjectcode']
		location 			= json.get('address_line1', '')
		ap 					= AddressParser()
		address 	 		= ap.parse_address(location)
		_lon 				= json.get('lon', None)
		_lat 				= json.get('lat', None)
		_lon_reported_from 	= json['lon_reported_from']
		_lat_reported_from 	= json['lat_reported_from']
		_time_reported		= json.get('time_reported', str(timestring.now()))
		_time_began 		= json.get('time_began', None)
		_time_ended 		= json.get('time_ended', None)
		_is_emergency 		= json.get('is_emergency', False)
		_description 		= json['description']
	except:
		return jsonify({'ERROR':'missing critical report information'})

	if not _lat and _lon or not location:
		return jsonify({'ERROR':'missing critical report information'})

	_user_id 			= cn_users.get_userid(session, token)
	if not (_lat and _lon) and location:
		location+=', Columbus OH'
		ll = get_lonlat(location)
		if ll:
			_lon = ll[0]
			_lat = ll[1]
		else:
			return jsonify({'ERROR':'bad location'})

	if not _user_id:
		return jsonify({'ERROR':'bad token'})

	report = CN_Report(title=_title, subjectcode=_subjectcode, house_number=address.house_number,\
		street_prefix=address.street_prefix, street=address.street, street_suffix=address.street_suffix,\
		apartment=address.apartment, lon=_lon, lat=_lat, lon_reported_from=_lon_reported_from,\
		lat_reported_from=_lat_reported_from, time_reported=_time_reported, time_began=_time_began, \
		time_ended=_time_ended, is_emergency=_is_emergency, description=_description, user_id=_user_id,\
		spam_count=0, score=25)
	session.add(report)
	try:
		session.commit()
	except:
		session.rollback()
	json["id"] = str(report.id)
	if not cn_perpetrators.make_perpetrators(session, json):
		remove_problem_report(session, json)
		return jsonify({'ERROR':'perpetrators may be missing information'})
	if not cn_report_orc.make_offenses(session, json):
		remove_problem_report(session, json)
		return jsonify({'ERROR':'offenses may be missing information'})
	if not cn_property.make_property(session, json):
		remove_problem_report(session, json)
		return jsonify({'ERROR':'property may be missing information'})
	calculate_score(session, report.id)
	return jsonify({'id':str(report.id)})


def delete_report(session, json):
	token	 			= json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})

	if not cn_users.get_userid(session, token):
		return jsonify({'ERROR':'bad token'})

	_id = json.get('id', None)
	if not _id:
		return jsonify({'ERROR':'no report id'})

	#delete everything that depends on report
	prop = session.query(cn_property.CN_StolenProperty)\
	.filter(cn_property.CN_StolenProperty.reportID == str(_id)).delete()
	offe = session.query(cn_report_orc.CN_Report_OhioRevisedCode)\
	.filter(cn_report_orc.CN_Report_OhioRevisedCode.report == str(_id)).delete()
	perp = session.query(cn_perpetrators.CN_Perpetrator)\
	.filter(cn_perpetrators.CN_Perpetrator.reportID == str(_id)).delete()
	comm = session.query(cn_comments.CN_Comments)\
	.filter(cn_comments.CN_Comments.reportID == str(_id)).delete()

	#delete report
	q = session.query(CN_Report).filter(CN_Report.id == str(_id)).delete()
	if not q:
		return jsonify({'ERROR':'bad report id'})
	session.commit()
	return jsonify({'result':'true', 'deleted':[{'property':str(prop), 'offenses':str(offe), 'perpetrators':str(perp), 'comments':str(comm)}]})



def remove_problem_report(session, json):
	token	 			= json.get('token', None)
	if not token:
		return False

	if not cn_users.get_userid(session, token):
		return False

	_id = json.get('id', None)
	if not _id:
		return False

	#delete everything that depends on report
	prop = session.query(cn_property.CN_StolenProperty)\
	.filter(cn_property.CN_StolenProperty.reportID == str(_id)).delete()
	offe = session.query(cn_report_orc.CN_Report_OhioRevisedCode)\
	.filter(cn_report_orc.CN_Report_OhioRevisedCode.report == str(_id)).delete()
	perp = session.query(cn_perpetrators.CN_Perpetrator)\
	.filter(cn_perpetrators.CN_Perpetrator.reportID == str(_id)).delete()
	comm = session.query(cn_comments.CN_Comments)\
	.filter(cn_comments.CN_Comments.reportID == str(_id)).delete()

	#delete report
	q = session.query(CN_Report).filter(CN_Report.id == str(_id)).delete()
	if not q:
		return False
	session.commit()
	return True
	

def get_report(session, reportid):
	reports = session.query(CN_Report).filter(CN_Report.id == reportid).all()
	if not reports:
		return None
	else:
		return reports[0]