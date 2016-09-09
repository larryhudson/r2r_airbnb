from flask import Flask, render_template, request
import search_functions as SF
import foursquare as FSQ
from os import environ
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/search', methods=['POST'])
def bnb_search():
    city = request.form['city']
    airbnb_response = SF.get_airbnb_response(city)
    average_price = SF.get_average_price(airbnb_response)
    return render_template('average_price.html',
                            city=city,
                            average_price=average_price)


@app.route('/result', methods=['POST'])
def results():
    price_min = request.form['price_min']
    price_max = request.form['price_max']
    price_range = (int(price_min), int(price_max))
    city = request.form['city']
    maps_api_key = environ["MAPS_API_KEY"]

    airbnb_response = SF.get_airbnb_response(city, price_range)
    listings = SF.get_top_listings(airbnb_response)

    colours_dict = {'Entire home/apt': 'red',
                    'Private room': 'blue',
                    'Shared room': 'yellow'
    }               
    first_lat = listings[0]['lat']
    first_lng = listings[0]['lng']

    return render_template('result.html', listings=listings, first_lat=first_lat, first_lng=first_lng, maps_api_key=maps_api_key, colours_dict=colours_dict)

@app.route('/foursquare/<airbnb_id>')
def foursquare(airbnb_id):
    airbnb_listing_response = SF.get_airbnb_listing_response(airbnb_id)
    airbnb_lat_lng = SF.get_airbnb_lat_lng(airbnb_listing_response)
    airbnb_lat, airbnb_lng = airbnb_lat_lng
    maps_api_key = environ["MAPS_API_KEY"]
    colours_dict = {'Food': 'blue',
                    'Outdoors & Recreation': 'green',
                    'Event': 'red',
                    'Professional & Other Places': 'orange',
                    'Residence': 'yellow',
                    'Nightlife Spot': 'purple',
                    'Arts & Entertainment': 'purple',
                    'College & University': 'orange',
                    'Shop & Service': 'red',
                    'Travel & Transport': 'green',
                    }

    response = FSQ.venue_explore_response(airbnb_lat_lng)
    places = FSQ.get_recommended_places(response)

    return render_template('foursquare.html', airbnb_lat=airbnb_lat, airbnb_lng=airbnb_lng, places=places, maps_api_key=maps_api_key, colours_dict=colours_dict)


@app.route('/map')
def map():
    return render_template('map.html')
