from sqlalchemy import Column, Integer, String, Float
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from flask import Flask, jsonify, request
import cn_reports
import cn_users


class CN_Comments(Base):
	__tablename__	= 'cn_comments'

	id 				= Column(Integer, primary_key=True)
	reportID		= Column(Integer, ForeignKey('cn_reports.id'))
	content 		= Column(String)
	userid 			= Column(Integer, ForeignKey('cn_users.id'))

	report = relationship("CN_Report", backref=backref('cn_comments'))


def make_comment(session, json):
	token = json.get('token', None)
	if not token:
		return jsonify({'ERROR':'token missing'})

	_userid = cn_users.get_userid(session, token)
	if not _userid:
		return jsonify({'ERROR':'bad token'})

	_reportID = json.get('report_id', None)
	if not _reportID:
		return jsonify({'ERROR':'no report_id'})

	_content  = json.get('content', None)
	if not _content:
		return jsonify({'ERROR':'no content given or content is empty'})

	comment   = CN_Comments(reportID=_reportID, content=_content, userid=_userid)
	session.add(comment)
	try:
		session.commit()
	except:
		session.rollback()
		return jsonify({'ERROR':'report id may be invalid'})
	cn_reports.calculate_score(session, _reportID)
	return jsonify({'result':'true'})





'''
{  
   "token":"1d44bb7d-f8d7-4326-aae3-3acc0e4e1835",
   "report_id": "15",
   "content":"this is another comment to see if the system works"
}
'''
