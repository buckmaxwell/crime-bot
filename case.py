from sqlalchemy import Column, Integer, String, Float, DateTime
from bs4 import BeautifulSoup as bs
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
#mine
import db
from db import Base


class Case(Base):
	__tablename__='cases'

	id 			= 	Column(Integer, primary_key=True)
	number 		= 	Column(String)
	title 		= 	Column(String)
	report_no 	= 	Column(String)
	subjectcode = 	Column(String, ForeignKey('subjects.code'))
	house_number= 	Column(String)
	street_prefix = Column(String)
	street 		= 	Column(String)
	street_suffix = Column(String)
	apartment 	= 	Column(Integer)
	city 		= 	Column(String)
	zone 		= 	Column(Integer)
	precinct 	=	Column(Integer)
	district 	= 	Column(Integer)
	crime_began = 	Column(DateTime)
	crime_ended = 	Column(DateTime)
	report_date = 	Column(DateTime)
	badge 	 	=	Column(Integer, ForeignKey('officers.badge'))
	description = 	Column(String)

	officer = relationship("Officer", backref=backref('cases'))
	subject = relationship("Subject", backref=backref('cases'))

	#all the below should be able to be fetched via the connection tables
	#offenses = #array of offenses, [[int, string], [int, string],...]
	#victims = Column(ARRAY(Integer))
	#arrestees = Column(ARRAY(Integer))
	#stolen_property = may not need -- property has a caseID attatched so query.filter(Property.caseID = id)