import requests
from address import AddressParser, Address
#uncomment to create tables
import db_create
import db
from db import Base
#packages built from police data
import subject
import offenses
import property
#user tables (are these necessary imports?)
import cn_users
import cn_reports
import cn_property
import cn_perpetrators
import cn_report_orc
import cn_comments
import cn_spamreport_user
import cn_feed
#
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import update

import sys, os
from sqlalchemy import desc


