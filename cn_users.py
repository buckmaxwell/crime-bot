from sqlalchemy import Column, Integer, String, Numeric, Boolean, update
import uuid
from sqlalchemy_utils import UUIDType
#mine
import db
from db import Base
from sqlalchemy import ForeignKey
#pass hash
from Crypto.Hash import SHA256
from flask import Flask, jsonify, request

#ADMIN TOKEN: c4d78a0b-6e2a-4ddd-b87f-3fc70aba1d26

class CN_User(Base):
	__tablename__	= 'cn_users'

	id 				= Column(Integer, 		primary_key=True)
	username		= Column(String,	 	unique=True)
	passwordhash	= Column(String)
	token			= Column(UUIDType, 		default=uuid.uuid4())
	active			= Column(Boolean)

class TempHash(Base):
	__tablename__	= 'temp_hash'

	id				= Column(Integer, 		primary_key=True)
	temphash 		= Column(String)


def generate_hash(password):
	newhash = SHA256.new()
	newhash.update(password)
	return buffer(newhash.digest())


def make_cnuser(session, _username, _password, _active):
	#Check if user exists
	if session.query(CN_User).filter(CN_User.username == _username).all():
		return jsonify({'ERROR':'username already in use'})
	#Make user
	_passwordhash 	= generate_hash(_password)
	user 			= CN_User(username=_username, passwordhash=_passwordhash, active=_active)
	session.add(user)
	session.commit()
	result 	= {
				        'id'			: user.id,
				        'username'		: user.username,
				        'token'			: str(user.token),
						'active'		: user.active
			  }
	return jsonify(result)

def get_token(session, _username, _password):
	user = session.query(CN_User).filter(CN_User.username == _username).all()
	session.query(TempHash).filter(1==1).delete()
	session.commit()
	if user:
		_passwordhash 	= generate_hash(_password)
		ph = TempHash(temphash=_passwordhash,)
		session.add(ph)
		session.commit()
		if user[0].passwordhash == ph.temphash:
			return jsonify({'token':str(user[0].token)})
		else:
			return jsonify({'ERROR':'incorrect password'})
	else:
		return jsonify({'ERROR':'username does not exist'})

def change_token(session, _token):
	conn = db.get_engine().connect()
	stmt = update(CN_User).where(CN_User.token == _token).values(token=uuid.uuid4())
	conn.execute(stmt)
	conn.close()
	return jsonify({'result':'true'})

def get_userid(session, token):
	user = session.query(CN_User).filter(CN_User.token == token).all()[0]
	if user:
		return user.id
	else:
		return False





