from sqlalchemy import Column, Integer, String, Float
from bs4 import BeautifulSoup as bs
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
#mine
import db
from db import Base

class PropertyType(Base):
	__tablename__ = 'property_types'

	code = Column(Integer, primary_key=True)
	description = Column(String)


class StolenProperty(Base):
	__tablename__ = 'stolen_property'

	id = Column(Integer, primary_key=True)
	code = Column(Integer, ForeignKey('property_types.code'))
	manufacturer = Column(String)
	model = Column(String)
	description = Column(String)
	value = Column(Float) # .strip('$ ')
	caseID = Column(Integer, ForeignKey('cases.id'))

	case = relationship("Case", backref=backref('stolen_property'))
	property_type = relationship("PropertyType", backref=backref('stolen_property'))