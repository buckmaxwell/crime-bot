from sqlalchemy import Column, Integer, String
#mine
import db
from db import Base

class Subject(Base):
	__tablename__ = 'subjects'
	
	code = Column(String, primary_key=True)
	description = Column(String)
