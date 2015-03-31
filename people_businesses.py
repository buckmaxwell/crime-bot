from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from bs4 import BeautifulSoup as bs
from nameparser import HumanName
from address import AddressParser, Address
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
#mine
import db
from db import Base
#
#age manip
import timestring
#
from fuzzywuzzy import fuzz

#TODO: change vars for make_person and get rid of all the damn V's


class Person(Base):
	__tablename__='people'

	id = Column(Integer, primary_key=True)
	fname = Column(String)
	lname = Column(String)
	mname = Column(String)
	name_suffix = Column(String)
	name_title = Column(String)
	sex = Column(String)
	race = Column(String)
	dob_est = Column(DateTime)
	house_number = Column(String)
	street_prefix = Column(String)
	street = Column(String)
	street_suffix = Column(String)
	apartment = Column(String)
	zip = Column(String)
	victim = Column(Boolean)
	arrestee = Column(Boolean)

class Business(Base):
	__tablename__='businesses'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	house_number = Column(String)
	street_prefix = Column(String)
	street = Column(String)
	street_suffix = Column(String)
	apartment = Column(String)
	zip = Column(String)

class Case_Person(Base):
	__tablename__ = 'case_person'

	case = Column(Integer, ForeignKey('cases.id'), primary_key=True )
	person = Column(Integer, ForeignKey('people.id'), primary_key=True)
	is_victim = Column(Boolean)



class Case_Business(Base):
	__tablename__ = 'case_business'

	case = Column(Integer, primary_key=True)
	business = Column(Integer, primary_key=True)