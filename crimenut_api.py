import requests
from address import AddressParser, Address
#uncomment to create tables
import db_create
import db
from db import Base
#packages built from police data
import subject
import offenses
import property
#user tables (are these necessary imports?)
import cn_users
import cn_reports
import cn_property
import cn_perpetrators
import cn_report_orc
import cn_comments
import cn_spamreport_user
import cn_feed
#
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import update

import sys, os
from sqlalchemy import desc
#FLASK
from flask import Flask, jsonify, request

app = Flask(__name__)

session = db.setup_session()

#index
@app.route('/', methods=['GET'])
def hello():
	return "This is the crimenut api."

#users
@app.route('/users/new', methods=['POST'])
def make_user():
	username 	= request.json['username']
	password 	= request.json['password']
	active		= True
	return cn_users.make_cnuser(session, username, password, active)


@app.route('/users/login', methods=['POST'])
def login():	
	try:
		username 	= request.json['username']
		password 	= request.json['password']
		return cn_users.get_token(session, username, password)
	except Exception as e:
		return jsonify({'ERROR':str(e)})


@app.route('/users/logout', methods=['POST'])
def logout():
	token = request.json['token']
	return cn_users.change_token(session, token)

#reports
@app.route('/reports/new', methods=['POST'])
def make_report():
	return cn_reports.make_report(session, request.json)

@app.route('/reports/delete', methods=['POST'])
def delete_report():
	return cn_reports.delete_report(session, request.json)

@app.route('/reports/comments/new', methods=['POST'])
def add_comment():
	return cn_comments.make_comment(session, request.json)

#perpetrators--can be given in report.  this is for adding additional perps
@app.route('/reports/perpetrators/new', methods=['POST'])
def add_perpetrators():
	return cn_perpetrators.add_perpetrators(session, request.json)

#offenses--can be given in report. this is for adding additional offenses
@app.route('/reports/offenses/new', methods=['POST'])
def add_offenses():
	return cn_report_orc.add_offenses(session, request.json)

#property--can be given in report. this is for adding additional property
@app.route('/reports/property/new', methods=['POST'])
def add_property():
	return cn_property.add_property(session, request.json)

@app.route('/reports/spam/new', methods=['POST'])
def report_spam():
	return cn_spamreport_user.report_spam(session, request.json)

@app.route('/reports/feed', methods=['POST'])
def get_feed():
	return cn_feed.get_feed(session, request.json)

@app.route('/reports/report', methods=['POST'])
def get_individual_report():
	return cn_feed.get_report(session, request.json)
'''
@app.route('/reports/feed', methods=['POST'])
def get_feed():

select trunc(extract(epoch from now() - timestamp '2015-03-15 11:54:00')/3600);
#feed
order by score - trunc(extract(epoch from now() - timestamp '2015-03-15 11:54:00')/3600) 

order_by(cn_reports.CN_Report.score - )
##
func.trunc(extract('epoch', now() - 'timestamp', cn_reports.CN_Report.report_time))/3600

'''

#nohup crimenut_api.py > log.txt 2>&1 &
###
#FLASK -- should be port 10122, temp switch to 10199 so as not to disrupt allen
###
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=10122, debug=True)

