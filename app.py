# Imports
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflecting the existing database into a new model
Base = automap_base()

# Using the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Saving references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Home route listing all available api routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Surfs Up Climate API<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"  
        f"<br/> Data available from 2010-01-01 to 2017-08-22"  
    )


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Creating our session (link) from Python to the DB
    session = Session(engine)

    # Finding the last data point in the DB
    last_data_point = session.query(Measurement.date).\
            order_by(Measurement.date.desc()).first()

    last_date = dt.datetime.strptime(last_data_point[0], "%Y-%m-%d")

    # Finding the date a year from the last point in the data set
    year_ago = dt.date(last_date.year, last_date.month, last_date.day) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()

    # Closing the session
    session.close

    # Detailing the last year of rain data with date/prcp dictionary
    date_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        date_prcp.append(prcp_dict)

    return jsonify(date_prcp)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Creating our session (link) from Python to the DB
    session = Session(engine)

    stations = session.query(Station.station, Station.name)

    # Closing the session
    session.close

    # Return a JSON list of stations from the dataset.
    station_id_name = []
    for station, name in stations:
        station_dict = {}
        station_dict["station id"] = station
        station_dict["station name"] = name
        station_id_name.append(station_dict)

    return jsonify(station_id_name)


# Observed temperatures route
@app.route("/api/v1.0/tobs")
def most_active():

    # Creating our session (link) from Python to the DB
    session = Session(engine)

    # ranking the stations by number of observations
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()
    
    # Isolating the id of the most active station
    most_active_station = active_stations[0][0]

    # Finding the name of the most active station
    name_most_active_station = (session.query(Station.name).\
        filter(Station.station == most_active_station).first())[0]

    # Finding the last data point in the DB
    last_data_point = session.query(Measurement.date).\
            order_by(Measurement.date.desc()).first()

    last_date = dt.datetime.strptime(last_data_point[0], "%Y-%m-%d")

    # Finding the date a year from the last point in the data set
    year_ago = dt.date(last_date.year, last_date.month, last_date.day) - dt.timedelta(days=365)

    # Querying dates and temperature observations of the most active station for the last year of data.
    temp_most_active = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()

    # closing session
    session.close

    # Returning a JSON list of temperature observations (TOBS) for the previous year.
    temperatures = []
    for date, tobs in temp_most_active:
        temp_dict = {}
        temp_dict["station name"] = name_most_active_station
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temperatures.append(temp_dict)

    return jsonify(temperatures)

# start date route
@app.route("/api/v1.0/<start>")
# adding a variable 'start' to the function
def start(start):
    # Creating our session (link) from Python to the DB
    session = Session(engine)

    # altering format of user entered date
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    # maximum temperature
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).first()

    # Minimum temperature
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).first()

    # Average temperature
    avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).first()

    # closing session
    session.close

    start_dict = {"TMIN": min_temp, "TMAX": max_temp, "TAVG": avg_temp}

    return jsonify(start_dict)

# start and end date route
@app.route("/api/v1.0/<start>/<end>")
# adding variables 'start' and 'end' to the function
def start_end(start, end):
    # Creating our session (link) from Python to the DB
    session = Session(engine)

    # setting format of user entered start date
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    # setting format of user entered end date
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")

    # Maximum temperature
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).first()

    # Minimum temperature
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).first()

    # Average temperature
    avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).first()

    # closing session
    session.close

    start_end_dict = {"TMIN": min_temp, "TMAX": max_temp, "TAVG": avg_temp}

    return jsonify(start_end_dict)



if __name__ == '__main__':
    app.run(debug=True)

