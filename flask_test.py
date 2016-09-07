from flask import Flask, jsonify, render_template, request, redirect
import search_functions as SF
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

    first_lat = listings[0]['lat']
    first_lng = listings[0]['lng']

    return render_template('result.html', listings=listings, first_lat=first_lat, first_lng=first_lng, maps_api_key=maps_api_key)

@app.route('/map')
def map():
    return render_template('map.html')
