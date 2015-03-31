from sqlalchemy import create_engine

#
from db import Base
#import all
import property
import subject
import offenses
#
import cn_users
import cn_reports
import cn_property
import cn_perpetrators
import cn_report_orc
import cn_comments
import cn_spamreport_user
#
import db

#
#create user crimeapp with password 'wearethesuperhero500lovemax';
#create database crimedb with owner crimeapp;
#
db = db.get_engine()
#url = 'postgresql://%s:%s@localhost:5432/crimedb' % ('crimeapp', 'wearethesuperhero500lovemax')
#db = create_engine(url)
Base.metadata.create_all(bind=db) #is this the best place? gotta put this somewhere