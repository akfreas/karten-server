from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

Base = declarative_base()

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    revision = Column(Integer)
    date = Column(Date) 
    term = Column(String)
    definition = Column(String)

