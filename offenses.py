from sqlalchemy import Column, Integer, String, Numeric
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
import re

class Offense(Base):
	__tablename__='offenses'

	lcode = Column(Numeric, primary_key=True)
	lcode_ext = Column(String, primary_key=True)
	description = Column(String)
	completed = Column(String)#maybe should be bool or char

class OhioRevisedCode(Base):
	__tablename__='ohio_revised_codes'

	code = Column(Numeric, primary_key=True)
	link = Column(String)

class Case_Offense(Base):
	__tablename__ = 'case_offense'

	case = Column(Integer, primary_key=True)
	lcode = Column(Numeric, primary_key=True)
	lcode_ext = Column(String, primary_key=True)