from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", pool_pre_ping=True)
Base = automap_base()
Base.prepare(autoload_with=engine)

measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    """Available Routes"""
    return(
        f'/api/v1.0/precipitation'
        f'/api/v1.0/stations'
        f'/api/v1.0/tobs'
        f'/api/v1.0/<start>'
        f'/api/v1.0/<start>/<end>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

#filtering for most recent year of prcp data
    precipitation_data = session.query(measurement.date,measurement.prcp).filter(measurement.date >= "2016-08-23").filter(measurement.prcp != None).order_by(measurement.date).all()
    
    session.close()

#creating dictionaries containing precipitation data from query and appending results to a list
    precipitation_list = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        precipitation_list.append(precipitation_dict)

    return jsonify(precipitation_list)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    station_data = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation)
    session.close()

    #creating dictionaries with query results from station_data and appending the results to a list
    stations_list = []
    for station, name, latitude, longitude, elevation in station_data:
        station_dict = {}
        station_dict['ID'] = station
        station_dict['Name'] = name
        station_dict['Latitude'] = latitude
        station_dict['Longitude'] = longitude
        station_dict['Elevation'] = elevation
        stations_list.append(station_dict)
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    temp_data = session.query(measurement.date,measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= '2016-08-18').order_by(measurement.date).all()

    session.close()

    temp_list =[]
    for date, temp in temp_data:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['Temp']= temp
        temp_list.append(temp_dict)

    return jsonify(temp_list)

@app.route('/api/v1.0/<start>')
def start(start_date):
    session = Session(engine)
    temperature_stats = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date > start_date).all()
    session.close()
    try: 
        return(
                f'Lowest Temperature: {temperature_stats[0][0]}<br>'
                f'Highest Temperature: {temperature_stats[0][1]}<br>'
                f'Average Temperature: {temperature_stats[0][2],2}<br>'
        )

    except:
        return (
                f'Date provided not in range of data'
                f'The most recent data point was recorded in 2017-08-23, try another date before that'
        )

@app.route('/api/v1.0/<start>/<end>')
def start_end(startdate, enddate):

    session = Session(engine)
    temperature_stats2 = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs).filter(measurement.date >= startdate).filter(measurement.date<=enddate)).all()
    session.close()

    try:
        return (
                f'Lowest Temperature: {temperature_stats2[0][0]}<br>'
                f'Highest Temperature: {temperature_stats2[0][1]}<br>'
                f'Average Temperature: {temperature_stats2[0][2],2}<br>'
        )
    except:
        return (
                f'Date provided not in range of data'
                f'The most recent data point was recorded in 2017-08-23, try another date before that.'
    )
if __name__ == '__main__':
    app.run(debug=True)