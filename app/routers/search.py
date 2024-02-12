from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session

from models import Activity
from database import get_db
from es_utils import get_es_client, search_activities, index_activity
import logging




logger = logging.getLogger(__name__)

# Initialize the Elasticsearch client
es_client = get_es_client()

# Function to create the Elasticsearch index if it doesn't exist
def create_index(es_client):
    index_name = "activities"
    if not es_client.indices.exists(index=index_name):
        body = {
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "location": {"type": "text"},
                    "description": {"type": "text"}
                }
            }
        }
        es_client.indices.create(index=index_name, body=body)

# Function to index activities from the database into Elasticsearch
def index_activities_from_db(db: Session):
    try:
        # Retrieve activities from the database
        activities = db.query(Activity).all()
        
        # Index activities into Elasticsearch
        for activity in activities:
            index_activity(es_client, activity)

        return {"message": "Activities indexed successfully"}
    except Exception as e:
        # Log the error and raise an HTTPException with a 500 status code
        logger.exception("Error occurred during indexing")
        raise HTTPException(status_code=500, detail="Failed to index activities")

# Create a router instance for the search endpoints
router = APIRouter(
    prefix="/ElasticSearch",
    tags=['Search']
)

# Endpoint to search for activities
@router.get("/search/")
async def search_endpoint(query: str):
    try:
        # Perform search
        results = search_activities(es_client, query)  # Pass es_client argument
        return results
    except Exception as e:
        # Log the error and raise an HTTPException with a 500 status code
        logger.exception("Error occurred during search")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint to index activities from the database into Elasticsearch
@router.get("/index")
async def index_activities_handler(db: Session = Depends(get_db)):
    return index_activities_from_db(db)
