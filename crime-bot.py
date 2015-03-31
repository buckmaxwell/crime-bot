import db_create
import db
import json
import timestring
import requests
import case
from urllib2 import Request, urlopen, URLError

TOKEN = '1d44bb7d-f8d7-4326-aae3-3acc0e4e1835'

def get_lonlat(location):
	print location
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
	except Exception as e:
		print "get_lonlat(location):",e
	return lonlat


def make_cn_report(report, session):
	'''
	TODO: THIS IS FOR DEMO ONLY--INCOMPLETE
	'''
	address_line1 			= str(report.house_number)+" "+str(report.street_prefix)+" "+str(report.street)+" "+str(report.street_suffix)
	address_line1			= address_line1.replace('None','')
	lonlat  				= get_lonlat(address_line1+', Columbus OH')

	j 						= json.loads('{}')
	j["token"] 				= TOKEN
	j["subjectcode"] 		= report.subjectcode
	j["address_line1"]		= address_line1
	j["lon_reported_from"]	= lonlat[0]
	j["lat_reported_from"]  = lonlat[1]
	j["description"]		= report.description
	return j


def send_report(payload):
	r = requests.post('http://crimenut.maxwellbuck.com/reports/new', json=payload)
	resp = json.loads(r.text)
	try:
		x = resp["id"]
		return True
	except Exception as e:
		print e
		return False


def get_reports(session):
	yesterday = timestring.now()
	yesterday.day-=1
	reports = session.query(case.Case).filter(case.Case.report_date > str(yesterday)).all()
	for report in reports:
		try:
			r = make_cn_report(report, session)
			send_report(r)
		except Exception as e:
			print e


def start():
	session = db.setup_session()
	get_reports(session)


start()