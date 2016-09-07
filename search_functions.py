import json
import requests
from xml.etree import ElementTree as ET

########
# workflow plan
########
# we need to get the following from the user:
# home address
# where they want to go
# how long for
# when they wanna go? maybe just a month input?
# particular airbnb feature? wireless internet? rooms or entire apts?
# then it will do this:
# 01. search airbnb for available places
# airbnb Listings Search API
# 02. get average price per night
# build list of prices and get average
# or if there's a thing in the API
# 03. allow user to filter by price comma-separated
# create new list of listings that are within range
# 04. return top-rated places in that price range (maybe only a few) - based on
# number of reviews as well
# print list of titles, prices, maybe features? apt / room?
# 06. search rome2rio for routes from home address to lat/lng of chosen airbnb
# 07. return routes with durations, prices, types of transport
# (flight, train, whatever)
# maybe a rome2rio trip if that works?
# maybe a Google Maps thing
# 08. ask if user wants to add a stop
# if yes, go back to top
# if no, get directions from airbnb to home address

########
# airbnb
########
def get_airbnb_response(location, price_range=False, guests=1):
    url = "https://api.airbnb.com/v2/search_results" \
               + "?client_id=3092nxybyb0otqw18e8nh5nty" \
               + "&locale=en-AU" \
               + "&currency=AUD" \
               + "&_format=for_search_results_with_minimal_pricing" \
               + "&_offset=0" \
               + "&fetch_facets=true" \
               + "&guests=" + str(guests) \
               + "&checkin_date=2016-11-01" \
               + "&checkout_date=2016-11-08" \
               + "&ib=false" \
               + "&ib_add_photo_flow=true" \
               + "&location=" + location \
               + "&min_bathrooms=0" \
               + "&min_bedrooms=0" \
               + "&min_beds=1" \
               + "&min_num_pic_urls=10" \
               + "&sort=1"

    if price_range:
        price_min, price_max = price_range
        url += "&price_max=" + str(price_max) \
            + "&price_min=" + str(price_min)

    return json.loads(requests.get(url).text)

def get_airbnb_listing_response(id):
    url = "https://api.airbnb.com/v2/listings/" + str(id) \
        + "?client_id=3092nxybyb0otqw18e8nh5nty" \
        + "&locale=en-AU" \
        + "&currency=AUD" \
        + "&_format=v1_legacy_for_p3" \
        + "&_source=mobile_p3" \
        + "&number_of_guests=1"

    return json.loads(requests.get(url).text)

def get_airbnb_lat_lng(response):
    listing_response = response['listing']

    return(listing_response['lat'], listing_response['lng'])

def get_top_listings(response):
    listings_dict = response['search_results']
    listings = []
    for item in listings_dict:
        if item['listing']['star_rating'] and item['listing']['reviews_count']:
            listings.append({ 'id': item['listing']['id'], \
                              'title': item['listing']['name'] , \
                              'address': item['listing']['public_address'], \
                              'star_rating': item['listing']['star_rating'], \
                              'reviews_count': item['listing']['reviews_count'], \
                              'sort_average': item['listing']['star_rating'] + (item['listing']['reviews_count'] / 10), \
                              'price': item['pricing_quote']['rate']['amount'],
                              'lat': item['listing']['lat'],
                              'lng': item['listing']['lng'], })

    sorted_listings = sorted(listings, key=lambda k: k['sort_average'], reverse=True)
    return sorted_listings

def get_average_price(response):
    return response['metadata']['price_histogram']['average_price']

def get_top_neighbourhoods(response):
    top_neighbourhoods = []
    if 'top_neighborhoods' in response['metadata']['facets']:
        for item in response['metadata']['facets']['top_neighborhoods']:
            top_neighbourhoods.append({'name': item['key'], \
                                       'count': item['count'], })
        top_neighbourhoods = sorted(top_neighbourhoods, key = lambda k: k['count'], reverse=True)
    else:
        return False
    return top_neighbourhoods

######
# rome2rio
########

def get_rome2rio_response(oName, dName):

    url = "http://<server>/api/1.4/json/" \
        + "?oName=" + oName \
        + "&dName=" + dName \
        + "&key=0" \
        + "&currencyCode=AUD"
    return json.loads(requests.get(url).text)

def get_directions(response):

    o_pos = (response['places'][0]['lat'], response['places'][0]['lng'])
    d_pos = (response['places'][1]['lat'], response['places'][1]['lng'])

    routes = response['routes']

    potential_routes = []
    for route in response['routes']:
        potential_routes.append({ 'low_price': route['indicativePrices']['priceLow'], \
                                  'high_price': route['indicativePrices']['priceHigh'], \
                                  'distance': route['distance'], \
                                  'duration': route['totalDuration'] })


def main():
    home_address = input("Where do you live? ")
    destination = input("Where do you want to go? ")

    airbnb_response = get_airbnb_response(destination)
    average_price = get_average_price(airbnb_response)
    print("Average price in {0}: ${1} per night".format(destination, str(average_price)))
    top_neighbourhoods = get_top_neighbourhoods(airbnb_response)
    if top_neighbourhoods:
        print("Top neighbourhoods in {0}:".format(destination))
        neighbourhood_counter = 1
        for item in top_neighbourhoods:
            print("{0}. {1} ({2} listings)".format(neighbourhood_counter, item['name'], item['count']))
            item['counter'] = neighbourhood_counter
            neighbourhood_counter += 1

        counter_input = input("Where do you want to go? ")

        for item in top_neighbourhoods:
            if int(counter_input) == item['counter']:
                destination2 = item['name'] + ", " + destination
                break
    else:
        destination2 = destination
    price_input = input("How much do you want to spend? (comma separated) ")

    prices_range = tuple(price_input.replace(" ", "").split(","))

    airbnb_response2 = get_airbnb_response(destination2, prices_range)
    listings = get_top_listings(airbnb_response2)

    listing_counter = 1
    print("Top listings in {0}:".format(destination2))
    for item in listings:
        print("{0}. {1} - ${2} per night - average rating {3} from {4} reviews".format(listing_counter, item['title'], item['price'], item['star_rating'], item['reviews_count']))
        item['counter'] = listing_counter
        listing_counter += 1

    counter_input = input("Choose a listing: ")

    for item in listings:
        if int(counter_input) == item['counter']:
            chosen_item = item
            break

    listing_response = get_airbnb_listing_response(chosen_item['id'])['listing']

    chosen_listing = {'id': listing_response['id'],
                       'title': listing_response['name'],
                       'address': listing_response['address'],
                       'amenities': listing_response['amenities'],
                       'room_type': listing_response['room_type'],
                       'description': listing_response['description'],
                       'lat': listing_response['lat'],
                       'lng': listing_response['lng']}

    print("Chosen listing: {0}".format(chosen_listing['title']))
    print("Airbnb link: https://www.airbnb.com.au/rooms/{0}".format(chosen_listing['id']))
    print("Room type: {0}".format(chosen_listing['room_type']))
    print("Address: {0}".format(chosen_listing['address']))
    amenities_string = ", ".join(chosen_listing['amenities'])
    print("Amenities: {0}".format(amenities_string))
    print("Lat/lng: {0}".format(chosen_listing['lat_lng']))

    return chosen_listing['lat_lng']

########
# foursquare
########

if __name__ == "__main__":
    main()
