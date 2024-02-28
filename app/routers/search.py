
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from algoliasearch.search_client import SearchClient
import models, schemas
from database import get_db
from datetime import time

router = APIRouter(
    prefix="/algolia",
    tags=['Algolia Integration']
)

# Initialize Algolia client
algolia_client = SearchClient.create()
algolia_index = algolia_client.init_index('activities')
index = algolia_client.init_index('activities')

# Function to serialize Activity objects to JSON
def serialize_activity(activity):
    serialized_time_slots = [
        {
            'id': slot.id,
            'start_time': slot.start_time.strftime('%H:%M:%S'),  # Convert time to string
            'end_time': slot.end_time.strftime('%H:%M:%S'),      # Convert time to string
            'is_available': slot.is_available,
            'max_capacity': slot.max_capacity
        }
        for slot in activity.time_slots
    ]
    return {
        'objectID': str(activity.id),  # Use activity id as objectID
        'id': activity.id,
        'name': activity.name,
        'description': activity.description,
        'location': activity.location,
        'price': activity.price,
        'image_url': activity.image_url,
        'provider_id': activity.provider_id,
        'likes': activity.likes,
        'time_slots': serialized_time_slots
    }

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=List[schemas.Activity])
def index_activity_in_algolia(db: Session = Depends(get_db)):
    # Fetch all activities from the database
    activities = db.query(models.Activity).all()
    if not activities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No activities found")

    # Serialize and index each activity in Algolia
    indexed_activities = []
    for activity in activities:
        serialized_activity = serialize_activity(activity)
        algolia_index.save_object(serialized_activity)
        indexed_activities.append(serialized_activity)

    return indexed_activities
@router.get("/search", response_model=List[schemas.Activity])
def search_activities_in_algolia(
    query: str,
):
    # Search for activities in Algolia
    response = algolia_index.search(query)

    # Extract and return search results
    hits = response['hits']
    return hits
