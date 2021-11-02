#################################################
# Imports
#################################################

import numpy as np

#import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import date

from flask import Flask, jsonify

#################################################
# Create a flask app
#################################################

app = Flask(__name__)

#################################################
# Setup DB connections
# create engine to hawaii.sqlite
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

#################################################
# reflect an existing database into a new model
# reflect the tables
# Save references to each table
#################################################

Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Define routes
#################################################
@app.route("/")
def index():

#This is the base route that returns api docs 

    return (f"<strong>The climate app has the following routes:</strong><br/>"
            f"<hr>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/startdate/<br/>"
            f"/api/v1.0/startdate/enddate"
            f"<hr>")
            

@app.route("/api/v1.0/precipitation")
def precipitation():
#This route returns precipitation data, date and precip reading 

    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    all_prcp = list(np.ravel(results))

    return jsonify(all_prcp)



@app.route("/api/v1.0/stations")
def stations():
#This route returns station data

    session = Session(engine)

    results = session.query(Station.name, Station.id, Station.longitude, Station.latitude, Station.station).all()
    
    session.close()
    
    all_station = list(np.ravel(results))

    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tobs():
#This route returns temperature data 

    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.tobs).all()
    
    session.close()

    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>/")
@app.route("/api/v1.0/<start>/<end>")
def datefilter(start, end=None):
 
#This route will return the min temp, average temp, and max temp for the date range
#If no end date is specified, it will use today's date 
    
    try:
        start = dt.datetime.strptime(start, "%Y-%m-%d").date()
        if end != None: 
            try:
                end = dt.datetime.strptime(end, "%Y-%m-%d").date()
                return jsonify(tempstats(start,end))
    
            except ValueError as ex:
                return jsonify({'end date error': str(ex)}), 400   # jsonify, if this is a json api
        else: 
            end = date.today() 
            return jsonify(tempstats(start,end))

    except ValueError as ex:
        return jsonify({'start date error': str(ex)}), 400   # jsonify, if this is a json api
 

def tempstats(start,end):
    session = Session(engine)
    
    lowesttemp = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).scalar()
    all_data = list(np.ravel(lowesttemp))

    avgtemp = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).scalar()
    avgtemp = list(np.ravel(avgtemp))
    all_data.append(avgtemp)

    highesttemp = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).scalar()
    highesttemp = list(np.ravel(highesttemp))
    all_data.append(highesttemp)
           
    session.close()
    return(all_data)

#################################################
# Define main behavior
#################################################

if __name__ == "__main__":
    app.run(debug=True)