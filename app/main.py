from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db, engine
from models import Base, TouristPlace, Vote
from pydantic import BaseModel

app = FastAPI()

# Create tables if they don't exist
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Pydantic schemas for request and response
class TouristPlaceCreate(BaseModel):
    name: str
    description: str

class VoteCreate(BaseModel):
    tourist_place_id: int

@app.post("/tourist-places/")
async def create_tourist_place(place: TouristPlaceCreate, db: AsyncSession = Depends(get_db)):
    new_place = TouristPlace(name=place.name, description=place.description)
    db.add(new_place)
    await db.commit()
    await db.refresh(new_place)
    return new_place

@app.post("/vote/")
async def vote_for_place(vote: VoteCreate, db: AsyncSession = Depends(get_db)):
    # Check if tourist place exists
    result = await db.execute(select(TouristPlace).filter_by(id=vote.tourist_place_id))
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=404, detail="Tourist place not found")

    # Create a new vote
    new_vote = Vote(tourist_place_id=vote.tourist_place_id)
    db.add(new_vote)
    await db.commit()
    await db.refresh(new_vote)
    return {"message": "Vote cast successfully"}

@app.get("/tourist-places/{place_id}/votes/")
async def get_votes(place_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TouristPlace).filter_by(id=place_id))
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=404, detail="Tourist place not found")
    
    votes_count = await db.execute(select(Vote).filter_by(tourist_place_id=place_id))
    return {"tourist_place": place.name, "votes": votes_count.rowcount}
