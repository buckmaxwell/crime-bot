import db
from db import Base
from flask import Flask, jsonify, request
from sqlalchemy import func, extract
#
from math import radians, cos, sin, asin, sqrt
#
import cn_reports
import cn_users
import json


def get_reports_in_bounding_box(session, lon, lat, miles):
	# 1 degree of latitude 	is about 69 miles
	# 1 degree of longitude is about cos(latitude)*69  (widest at equator -69 miles, shrinks to 0 at poles)

	degrees_lat = abs(float(miles)/69)
	degrees_lon = abs(float(miles)/(cos(float(lat))*69))

	top_lat_bound 		= float(lat)+degrees_lat
	bottom_lat_bound 	= float(lat)-degrees_lat

	top_lon_bound		= float(lon)+degrees_lon
	bottom_lon_bound	= float(lon)-degrees_lon

	reports = session.query(cn_reports.CN_Report).filter(cn_reports.CN_Report.lon > bottom_lon_bound)\
	.filter(cn_reports.CN_Report.lon < top_lon_bound).filter(cn_reports.CN_Report.lat > bottom_lat_bound)\
	.filter(cn_reports.CN_Report.lat < top_lat_bound)\
	.order_by((cn_reports.CN_Report.score - \
		(func.trunc(extract('epoch', (func.now() -  cn_reports.CN_Report.time_reported) )/3600)) ).desc() )\
	.limit(1000).all()

	return reports


def get_perps_array(report):
	perps = []
	for p in report.cn_perpetrators:
		perp 					= get_new_json()
		perp["id"] 				= str(p.id)
		perp["est_dob"] 		= str(p.est_dob)
		perp["sex"] 			= str(p.sex)
		perp["race"] 			= str(p.race)
		perp["p.description"] 	= str(p.description)
		perps.append(perp)
	return perps


def get_prop_array(report):
	props = []
	for p in report.cn_stolen_property:
		prop 					= get_new_json()
		prop["id"] 				= str(p.id)
		prop["code"] 			= str(p.code)
		prop["manufacturer"] 	= str(p.manufacturer)
		prop["model"] 			= str(p.model)
		prop["p.description"] 	= str(p.description)
		prop["p.value"] 		= str(p.value)
		props.append(prop)
	return props


def get_offenses_array(report):
	orcs = []
	for o in report.cn_report_ohio_revised_code:
		orc 					= get_new_json()
		orc["ohio_revised_code"]= str(o.ohio_revised_code)
		orc["link"]				= str(o.orc.link)
		orcs.append(orc)
	return orcs

def get_comments_array(report):
	comms = []
	for c in report.cn_comments:
		comm 					= get_new_json()
		comm["id"]				= str(c.id)
		comm["userid"]			= str(c.userid)
		comm["content"]			= str(c.content)
		comms.append(comm)
	return comms


def report_jsonify(report, feed=True):
	result = get_new_json()

	result["id"]	 			= str(report.id)
	result["userid"]			= str(report.user_id)
	result["title"]   			= str(report.title)
	result["subject"] 			= str(report.subject.description)
	result["house_number"]		= str(report.house_number)
	result["street_prefix"] 	= str(report.street_prefix)
	result["street"]			= str(report.street)
	result["street_suffix"] 	= str(report.street_suffix)
	result["apartment"]			= str(report.apartment)
	result["lon"]				= str(report.lon)
	result["lat"]				= str(report.lat)
	result["lon_reported_from"]	= str(report.lon_reported_from)
	result["lat_reported_from"] = str(report.lat_reported_from)
	result["time_reported"]		= str(report.time_reported)
	result["time_began"]		= str(report.time_began)
	result["time_ended"]		= str(report.time_ended)
	result["is_emergency"]		= str(report.is_emergency)
	result["spam_count"]		= str(report.spam_count)
	result["description"]		= str(report.description)

	if not feed:
		result["perpetrators"]		= get_perps_array(report)
		result["property"]			= get_prop_array(report)
		result["offenses"]			= get_offenses_array(report)
		result["comments"]			= get_comments_array(report)

	return result

def get_new_json():
	return json.loads('{}')

def get_feed(session, json):
	token = json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})

	if not cn_users.get_userid(session, token):
		return jsonify({'ERROR':'bad token'})

	miles = json.get('miles', 10)
	lon   = json.get('lon', None)
	lat   = json.get('lat', None)
	page  = json.get('page', 1)

	last_report  = int(page)*20
	first_report =  last_report - 20

	if not lon and lat:
		return jsonify({'ERROR':'no lon or lat given'})

	try:
		reports = get_reports_in_bounding_box(session, lon, lat, miles)
	except Exception as e:
		return jsonify({'ERROR':str(e)})


	if not reports:
		return jsonify({'result':'no reports for locality'})

	result = get_new_json()
	reps = []
	for i,r in enumerate(reports):
		if i >= first_report and i < last_report:
			reps.append(report_jsonify(r))
			
	result["reports"] = reps
	if len(reports) > last_report:
		result["next_page"] = int(page)+1
	if page != 1:
		result["prev_page"] = int(page)-1

	return jsonify(result)


def get_report(session, json):
	token	 = json.get('token', None)
	reportid = json.get('reportid', None)
	if not token:
		return jsonify({'ERROR':'token missing'})

	if not cn_users.get_userid(session, token):
		return jsonify({'ERROR':'bad token'})

	if not reportid:
		return jsonify({'ERROR':'no reportid given'})

	report = cn_reports.get_report(session, reportid)
	result = report_jsonify(report, False)
	if not result:
		return jsonify({'ERROR':'reportid does not exist'})
	return jsonify(result)




