from sqlalchemy import create_engine

#
from db import Base
#import all
import case
import people_businesses
import property
import subject
import officer
import offenses
import db

#
#create user crimeapp with password 'wearethesuperhero500lovemax';
#create database crimedb with owner crimeapp;
#
db = db.get_engine()
#url = 'postgresql://%s:%s@localhost:5432/crimedb' % ('crimeapp', 'wearethesuperhero500lovemax')
#db = create_engine(url)
Base.metadata.create_all(bind=db) #is this the best place? gotta put this somewhere