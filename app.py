##############################################
#Imports
###############################################
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

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Base.classes.keys() # Get the table names

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Create our session (link) from Python to the DB
#################################################
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

####################################################
# API DATA
# ##################################################
 
 # Returns the jsonified precipitation data for the last year in the database  
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recentdatestr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recentdate=dt.datetime.strptime(recentdatestr[0], '%Y-%m-%d')
    querydate = dt.date(recentdate.year -1, recentdate.month, recentdate.day)
    data = [Measurement.date,Measurement.prcp]
    querydata = session.query(*data).filter(Measurement.date >= querydate).all()
    precipitation_data = []
    session.close()

    for date, prcp in querydata:
        data = {}
        data['date'] = date #querydata[0]
        data['prcp'] = prcp #querydata[1]
        precipitation_data.append(data)

    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    data = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*data).all()
    session.close()

    stations_data = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations_data.append(station_dict)

    return jsonify(stations_data)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    recentdatestr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recentdate=dt.datetime.strptime(recentdatestr[0], '%Y-%m-%d')
    querydate = dt.date(recentdate.year -1, recentdate.month, recentdate.day)
    data = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*data).filter(Measurement.date >= querydate).all()

    session.close()
    tobs_data = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route('/api/v1.0/<start>')
def startdate(start):
    session = Session(engine)
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    start_data = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        start_data.append(tobs_dict)

    return jsonify(start_data)

#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    session = Session(engine)
    start = dt.datetime.strptime(start, '%Y-%m-%d')                     
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    startend_data = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        startend_data.append(tobs_dict)

    return jsonify(startend_data)


 #4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
