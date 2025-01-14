# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
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
# Homepage route
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return last 12 months of precipitation data."""
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    precipitation_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    stations_data = session.query(Station.station).all()
    stations_list = list(np.ravel(stations_data))

    return jsonify(stations_list)

# Temperature Observations (TOBS) route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most active station."""
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    tobs_data = (
        session.query(Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )

    tobs_list = list(np.ravel(tobs_data))

    return jsonify(tobs_list)


# Start route
@app.route("/api/v1.0/<start>")
def start(start):
    """Return min, avg, and max temperature for dates >= start."""
    temps = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .all()
    )
    temps_dict = {"TMIN": temps[0][0], "TAVG": temps[0][1], "TMAX": temps[0][2]}

    return jsonify(temps_dict)


# Start/End route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return min, avg, and max temperature for a date range."""
    temps = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )
    temps_dict = {"TMIN": temps[0][0], "TAVG": temps[0][1], "TMAX": temps[0][2]}

    return jsonify(temps_dict)

# Run
if __name__ == "__main__":
    app.run(debug=True)


















