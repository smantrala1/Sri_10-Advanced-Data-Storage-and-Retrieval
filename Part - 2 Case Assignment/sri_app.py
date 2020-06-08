# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 21:46:56 2020

@author: kalag
"""


# Home Page with all available routes`/`

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import pandas as pd
import datetime as dt


from flask import Flask, jsonify
#%%

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#%%

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#%%

Base.classes.keys()
#%%
# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#%%

session = Session(engine)

#%%

#start_d='2016-01-28'
#end_d ='2016-02-11'
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#%%
#################################################
# Flask Routes
#################################################
#%%
@app.route("/")
def welcome():
    """List all available api routes."""
    return("""<html>
    <h1>Welcome to Hawai Vacation API. Below are the available API routes: </h1>
    <br>
    <ul>
    <li>
    <Strong>Previous year's Precipitation:</Strong>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    
    <li>
    <Strong>List of Stations:</Strong>
    <a href="/api/v1.0/stations">/api/v1.0/stations</a>
    <br><br>
    <li>
    <Strong>Dates and temperature observations of the most active station for the last year of data:</Strong>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>

    
    <li>
    <Strong>
    List of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range:
    </Strong>
    <br>

        <ol>
        <li>
        
        Start Date:/api/v1.0/&lt;startdate&gt;
        <br>Example:<br>
        <a href="/api/v1.0/2016-01-28">/api/v1.0/2016-01-28</a>
        </li>
        <br>
        <li>
        
        Start Date and End Date:/api/v1.0/&lt;start-date&gt;/&lt;end-date&gt;
        <br>Example:<br>
        <a href="/api/v1.0/2016-01-28/2016-02-11">/api/v1.0/2016-01-28/2016-02-11</a>
        <br>
        </li>
        </ol></li>
    </ul>
</html>""")
        
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Docstring 
    """Return a list of precipitations from last year"""

    connection = engine.connect()
    max_date = connection.execute( "select max(date) from Measurement" )
    for i in max_date:
        maxdate=i[0]
    
    one_year_ago = dt.datetime.strptime(maxdate, "%Y-%m-%d") - dt.timedelta(days=366)


    oneyr_prcp = connection.execute('SELECT date,prcp FROM Measurement WHERE date >= :val', {'val': one_year_ago})


    #precipitation_dict = dict(results_precipitation)
    past_yr_prcp = []
    for date,prcp in oneyr_prcp:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Precipitation"] = prcp
        
        past_yr_prcp.append(temp_dict)
    return jsonify(past_yr_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Docstring 
    """Return a list unique stations"""

    conn = engine.connect()
    
    distinct_stations = pd.read_sql('SELECT distinct station from Measurement', conn)

    results_json = distinct_stations.to_json(orient='records')

    return results_json

@app.route("/api/v1.0/tobs")
def tobs():
    # Docstring 
    """Dates and temperature observations of the most active station for the last year of data"""
    #Previous year's Precipitation:
    connection = engine.connect()
    max_date = connection.execute( "select max(date) from Measurement" )
    for i in max_date:
        #print(i[0])
        maxdate=i[0]
        
    one_year_ago = dt.datetime.strptime(maxdate, "%Y-%m-%d") - dt.timedelta(days=366)
    one_year_ago
    
    
    max_station_id_data = connection.execute('select max(freq_count), station from \
                                                    (select count(station) as freq_count \
                                                            ,station \
                                                            from Measurement \
                                                            where station in (SELECT station \
                                                                                FROM Measurement \
                                                                                WHERE date >= :val) \
                                                            group by station \
                                                            order by count(station) desc)', {'val': one_year_ago})
    for i in max_station_id_data:
        max_station_id = i[1]
    
    #Query the last 12 months of temperature observation data for this station   
    max_station_oneyr_data = connection.execute('select date, tobs from Measurement \
                                                    WHERE date >= :val and \
                                                        station = :val2', {'val': one_year_ago, 'val2':max_station_id})
    
    past_yr_prcp = []    
    for date,tobs in max_station_oneyr_data:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature Obs"] = tobs
        
        past_yr_prcp.append(temp_dict)
    return jsonify(past_yr_prcp)


@app.route("/api/v1.0/<start>")
def start(start=None):

    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""
    connection = engine.connect()
    
    vacay_data_list = connection.execute('select date,min(tobs) as tmin,max(tobs) as tmax,avg(tobs) as tavg  \
                                                                                FROM Measurement \
                                                                                WHERE date >= :val group by date', {'val': start})
    
    start_date_prcp = []    
    for date,tmin,tmax,tavg in vacay_data_list:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Tmin"] = tmin
        temp_dict["Tmax"] = tmax
        temp_dict["Tavg"] = tavg
        
        start_date_prcp.append(temp_dict)
    return jsonify(start_date_prcp)


@app.route("/api/v1.0/<start>/<end>")
def startend(start=None,end=None):

    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""
    connection = engine.connect()
    
    vacay_data_list = connection.execute('select date,min(tobs) as tmin,max(tobs) as tmax,avg(tobs) as tavg  \
                                                                                FROM Measurement \
                                                                                WHERE date between :val and :val1 \
                                                                                    group by date', {'val': start,'val1':end})
    
    start_date_prcp = []    
    for date,tmin,tmax,tavg in vacay_data_list:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Tmin"] = tmin
        temp_dict["Tmax"] = tmax
        temp_dict["Tavg"] = tavg
        
        start_date_prcp.append(temp_dict)
    return jsonify(start_date_prcp)

if __name__ == "__main__":
    app.run(debug=True)