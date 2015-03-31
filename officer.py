from sqlalchemy import Column, Integer, String
from nameparser import HumanName
#mine
import db
from db import Base


class Officer(Base):
	__tablename__='officers'

	badge = Column(Integer, primary_key=True)
	title = Column(String)
	last_name = Column(String)