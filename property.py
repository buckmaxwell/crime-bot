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


def make_property_type(session, _code, _description):
	if not session.query(PropertyType).filter(PropertyType.code == _code).all():
		pt = PropertyType(code=_code, description=_description)
		session.add(pt)
		session.commit()

def make_stolen_property(session, _code, _manufacturer, _model, _description, _value, _caseID):
	sp = StolenProperty(code=_code, manufacturer=_manufacturer, model=_model, description=_description, \
	 value=_value, caseID=_caseID)
	session.add(sp)
	session.commit()
	return sp.id



def make_stolen_properties(session, pPrefix, caseID):
	#
	pStolenPropertiesPrimary = []
	#
	leng = len(pPrefix)
	i = 0
	while i < leng:
		try:
			pStolen = pPrefix[0 + i].text.strip()
			stolenPropArray = pStolen.split(' - ', 1)
			_code = int(stolenPropArray[0])
			_code_descrip = stolenPropArray[1]
			make_property_type(session, _code, _code_descrip)
			_manufacturer = pPrefix[4+i].text.strip()
			_model = pPrefix[5+i].text.strip()
			_description = pPrefix[10+i].text.strip()
			_value = float(pPrefix[11+i].text.strip('$ '))
			propID = make_stolen_property(session, _code, _manufacturer, _model, _description, _value, caseID)
			pStolenPropertiesPrimary.append(propID)
		except Exception as e:
			pass
		i+=13
	session.commit()
	return pStolenPropertiesPrimary


