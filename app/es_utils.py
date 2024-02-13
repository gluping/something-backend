from elasticsearch import Elasticsearch
import json


def get_es_client():

    es_client = Elasticsearch(


        "https://500328854aa34cfdb32aa3cfa721b8ee.us-central1.gcp.cloud.es.io:443",


        api_key=()

    )

    return es_client


def search_activities(es_client, query):
    """
    Perform search for activities in Elasticsearch.
    """
    index_name = "activities"

    # Search for activities
    response = es_client.search(
        index=index_name,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "location", "description"],
                    "fuzziness": "AUTO"  # Enable fuzzy matching
                }
            }
        }
    )

    # Extract and return search results
    return [hit["_source"] for hit in response["hits"]["hits"]]


def serialize_activity(activity):
    """
    Serialize Activity object to a JSON-serializable dictionary.
    """
    serialized_activity = {
        "id": activity.id,
        "name": activity.name,
        "description": activity.description,
        "location": activity.location,
        "price": activity.price,
        "image_url": activity.image_url,
        "provider_id": activity.provider_id,
        "likes": activity.likes
        # Add other attributes as needed
    }
    return serialized_activity

def index_activity(es_client, activity):
    """
    Index activity document in Elasticsearch.
    """
    index_name = "activities"
    
    # Serialize the activity object
    activity_dict = serialize_activity(activity)
    
    # Index the serialized activity into Elasticsearch
    es_client.index(index=index_name, body=activity_dict)