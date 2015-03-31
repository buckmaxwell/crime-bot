from sqlalchemy import Column, Integer, String, Numeric, Boolean, update
import uuid
from sqlalchemy_utils import UUIDType
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
#pass hash
from Crypto.Hash import SHA256
from flask import Flask, jsonify, request
import cn_reports
import cn_users

class CN_SpamReport_User(Base):
	__tablename__ 	= 'cn_spamreport_user'

	report 			= Column(Integer, ForeignKey('cn_reports.id'), primary_key=True)
	user 			= Column(Integer, ForeignKey('cn_users.id'), primary_key=True)


def report_spam(session, json):
	token = json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})
	userid = cn_users.get_userid(session, token)
	if not userid:
		return jsonify({'ERROR':'bad token'})
	
	reportid = json.get('reportid', None)
	if not reportid:
		return jsonify({'ERROR':'reportid missing'})
	report = cn_reports.get_report(session, reportid)
	if not report:
		return jsonify({'ERROR':'bad reportid'})
	report.spam_count+=1
	sr = CN_SpamReport_User(report=reportid, user=userid)
	session.add(sr)
	try:
		session.commit()
	except:
		session.rollback()
		return jsonify({'ERROR':'user already reported this post as spam'})
	cn_reports.calculate_score(session, reportid)
	return jsonify({'result':'true', 'spam_count':str(report.spam_count)})


'''
{
	"reportid":"15",
	"token":"1d44bb7d-f8d7-4326-aae3-3acc0e4e1835"
}
'''