from elasticsearch import Elasticsearch


def get_es_client():

    es_client = Elasticsearch(


        "https://500328854aa34cfdb32aa3cfa721b8ee.us-central1.gcp.cloud.es.io:443",


        api_key=("LfJEXo0Bg8CCZaeSTZCE", "ucE90FGPTNmGjHjkvTEiag")

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
                    "fields": ["name", "location", "description"]
                }
            }
        }
    )

    # Extract and return search results
    return [hit["_source"] for hit in response["hits"]["hits"]]

def index_activity(es_client, activity):
    """
    Index activity document in Elasticsearch.
    """
    index_name = "activities"
    es_client.index(index=index_name, body=activity)