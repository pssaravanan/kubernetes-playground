from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class TouristPlace(Base):
    __tablename__ = "tourist_places"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    tourist_place_id = Column(Integer, ForeignKey("tourist_places.id"))
    tourist_place = relationship("TouristPlace", back_populates="votes")

TouristPlace.votes = relationship("Vote", back_populates="tourist_place")
