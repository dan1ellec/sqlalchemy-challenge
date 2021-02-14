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
        f"Welcome to the Surfs Up Climate API"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        
    )


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Creating our session (link) from Python to the DB
    session = Session(engine)

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

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


if __name__ == '__main__':
    app.run(debug=True)

