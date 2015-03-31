from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
#mine
import db
from db import Base

class PropertyType(Base):
	__tablename__ = 'property_types'

	code = Column(Integer, primary_key=True)
	description = Column(String)