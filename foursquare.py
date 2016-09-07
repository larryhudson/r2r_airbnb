from os import environ
import requests
import json


def venue_explore_response(lat_lng_tuple):
    client_id = environ["FSQ_CID"]
    client_secret = environ["FSQ_CSEC"]

    url = "https://api.foursquare.com/v2/venues/explore" \
        + "?ll=" + str(lat_lng_tuple[0]) + "," + str(lat_lng_tuple[1]) \
        + "&llAcc=1000" \
        + "&limit=50" \
        + "&v=20160907" \
        + "&section=topPicks" \
        + "&m=foursquare" \
        + "&client_id=" + client_id \
        + "&client_secret=" + client_secret

    return json.loads(requests.get(url).text)['response']

def get_recommended_places(response):
    return response['groups'][0]['items']
