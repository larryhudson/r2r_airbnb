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

def buildcatdict(category_list):
    d = {}
    for category in category_list:
        cat_name = category['name']
        d[cat_name] = []
        for subcat in category['categories']:
            d[cat_name].append(subcat['name'])
            if 'categories' in subcat:
                for subsubcat in subcat['categories']:
                    d[cat_name].append(subsubcat['name'])
                    if 'categories' in subsubcat:
                        for subsubsubcat in subsubcat['categories']:
                            d[cat_name].append(subsubsubcat['name'])

    return d


def get_categories_response():
    client_id = environ["FSQ_CID"]
    client_secret = environ["FSQ_CSEC"]

    url = "https://api.foursquare.com/v2/venues/categories" \
        + "?m=foursquare" \
        + "&v=20160907" \
        + "&client_id=" + client_id \
        + "&client_secret=" + client_secret

    cats_list = json.loads(requests.get(url).text)['response']['categories']

    cats_dict = buildcatdict(cats_list)
    return cats_dict

def get_broad_category(category_dict, category):
    for broad_cat in category_dict:
        if category in category_dict[broad_cat]:
            return broad_cat

def get_recommended_places(response):
    categories_response = get_categories_response()
    places_list = response['groups'][0]['items']

    for place in places_list:
        place_cat = place['venue']['categories'][0]['name']
        place['broad_cat'] = get_broad_category(categories_response, place_cat)
        if 'tips' in place:
            place_tip = place['tips'][0]['text']
        else:
            place_tip = "No tips found"
        place['tip'] = place_tip

    return places_list
