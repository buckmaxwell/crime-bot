from sqlalchemy import Column, Integer, String, Numeric
#mine
import db
from db import Base
from sqlalchemy import ForeignKey

class OhioRevisedCode(Base):
	__tablename__='ohio_revised_codes'

	code = Column(Numeric, primary_key=True)
	link = Column(String)