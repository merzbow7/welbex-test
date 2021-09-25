from datetime import datetime

from sqlalchemy import Date, Column, Integer, String

from app import db


class Welbextest(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    date = Column(Date())
    count = Column(Integer())
    distance = Column(Integer)
