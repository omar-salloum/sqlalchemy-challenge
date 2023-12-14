# Import the dependencies.
import numpy as np
import pandas as pd
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

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=366)

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()

    session.close()

    prcp_analysis = {}
    for row in query:
        prcp_analysis[row[0]] = row[1]

    return jsonify(prcp_analysis)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    query = session.query(station.station).all()
    
    session.close()

    stat_list = [row[0] for row in query]
    return jsonify(stat_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= year_ago).all()
    
    session.close()

    tobs_list = [row[0] for row in query]
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def starting(start):
    try:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
    except ValueError:
        try:
            start_date = dt.datetime.strptime(start, "%Y,%m,%d")
        except ValueError:
            start_date = dt.datetime.strptime(start, "%Y%m%d")

    session = Session(engine)
    query = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start_date).all()
    session.close()

    start_dict = {}
    for row in query:
        start_dict['TMIN'] = row[0]
        start_dict['TMAX'] = row[1]
        start_dict['TAVG'] = row[2]

    return start_dict


@app.route("/api/v1.0/<start>/<end>")
def complete(start, end):
    try:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
    except ValueError:
        try:
            start_date = dt.datetime.strptime(start, "%Y,%m,%d")
        except ValueError:
            start_date = dt.datetime.strptime(start, "%Y%m%d")

    try:
        end_date = dt.datetime.strptime(end, "%m%d%Y")
    except ValueError:
        try:
            end_date = dt.datetime.strptime(end, "%Y,%m,%d")
        except ValueError:
            end_date = dt.datetime.strptime(end, "%Y%m%d")

    session = Session(engine)
    query = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    start_end_dict = {}
    for row in query:
        start_end_dict['TMIN'] = row[0]
        start_end_dict['TMAX'] = row[1]
        start_end_dict['TAVG'] = row[2]

    return start_end_dict



if __name__ == '__main__':
    app.run(debug=True)