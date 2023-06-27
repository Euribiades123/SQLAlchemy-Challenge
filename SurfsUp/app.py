# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt
import numpy as np
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine= create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#Now that you’ve completed your initial analysis, you’ll design a Flask API based on the queries that you just developed. To do so, use Flask to create your routes as follows:
# 1 - Start at the homepage - List all the available routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the SQLAlchemy Challenge<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
## 2. Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
#from climate_starter import get_precipitation_data
@app.route("/api/v1.0/precipitation")
def precipitation():
   
       # Design a query to retrieve the last 12 months of precipitation data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
     
    # Calculate the date one year from the last date in data set
    latest_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    start_date = latest_date - dt.timedelta(days=365)
    # Query the Measurement table for precipitation data within the last 12 months
    precipitation = session.query(Measurement.prcp, Measurement.date).\
        filter(Measurement.date >= start_date).all()
    # Create a dictionary from the row data and append to a list of precipitation_query_values
    precipitation_values = []
    for date, prcp in precipitation:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = prcp
        precipitation_values.append(precipitation_dict)
    # Return a JSON list of precipitation_query_values
    session.close()
    return jsonify(precipitation_values)
    

# 3. /api/v1.0/stations Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    stations_list = list(np.ravel(stations))
    session.close()
    return jsonify(stations_list)
   

# 4. /api/v1.0/tobs Query the dates and temperature observations of the most-active station for the previous year of data.
        #Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the most recent date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()
    
    # Query temperature observations for the previous year for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Create a list of dictionaries to store the date and temperature observations
    temperature_list = []
    for date, tobs in temperature_data:
        temperature_list.append({"date": date, "tobs": tobs})
  
    session.close()
    return jsonify(temperature_list)


# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
        #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
        #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
        #For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date == start).all()

    # Create a dictionary to store the temperature statistics
    stats_dict = {
        "start_date": start,
        "end_date": session.query(func.max(Measurement.date)).first()[0],
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }
    session.close()
    return jsonify(stats_dict)


@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_range(start, end):
    # Query the minimum, average, and maximum temperatures for dates within the start-end range
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create a dictionary to store the temperature statistics
    stats_dict = {
        "start_date": start,
        "end_date": end,
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }
    session.close()
    return jsonify(stats_dict)



if __name__ == '__main__':
    app.run(debug=True)