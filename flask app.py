


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
session = Session(engine)

Station = Base.classes.station
Measurement = Base.classes.measurement

date_1_year_ago = dt.date(2017,8,23) - dt.timedelta(weeks =52)


#precipitation data

past_year_data = session.query(Measurement.date, Measurement.prcp).\
                filter(func.strftime(Measurement.date) > date_1_year_ago).all()

past_year_data_df = pd.DataFrame(past_year_data, columns = ["date", "prcp"])


past_year_data_df.set_index("date", inplace = True)

past_year_data_df.dropna(inplace = True)

past_year_data_df.sort_index(inplace = True)


#stations data


stations_df = pd.read_sql("SELECT * FROM station", engine)

stations_df = stations_df[["station", "name", "latitude", "longitude", "elevation"]]
stations_df.set_index("station", inplace = True)



#tobs data



past_year_data_tobs = session.query( Measurement.tobs,Measurement.date ).\
                filter(func.strftime(Measurement.date) > date_1_year_ago).\
                filter(Measurement.station == "USC00519281").all()


past_year_data_tobs = pd.DataFrame(past_year_data_tobs, columns = ["tobs", "date"])

past_year_data_tobs.set_index("date", inplace = True)



#start-end data

all_prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(func.strftime(Measurement.date) > date_1_year_ago).all()

all_prcp_data_df = pd.DataFrame(all_prcp_data, columns = ["date", "prcp"])




##app


app = Flask(__name__)

@app.route("/")
def welcome():
    return("1")



@app.route("/api/v1.0/precipitation")
def precipitation():
    return jsonify(past_year_data_df.to_dict())




@app.route("/api/v1.0/stations")
def stations():
    return jsonify(stations_df.to_dict())


@app.route("/api/v1.0/tobs")
def tobs():
    return jsonify(past_year_data_tobs.to_dict())



@app.route("/api/v1.0/<start>")
def start(start):


    
    all_prcp_data_start_date_df = all_prcp_data_df.loc[all_prcp_data_df["date"]>start]


    min_temp = all_prcp_data_start_date_df["prcp"].min()
    max_temp = all_prcp_data_start_date_df["prcp"].max()

    avag_temp = all_prcp_data_start_date_df["prcp"].mean()
    
    
    if all_prcp_data_start_date_df["prcp"].count() == 0:
        return("Date out of range")  
    else: return(jsonify({"Min Tempture": min_temp, "Max Tempture": max_temp, "Averge Tempture": avag_temp}))

            



@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    

    all_prcp_data_start_end_date_df = all_prcp_data_df.loc[all_prcp_data_df["date"]> start]
    
    all_prcp_data_start_end_date_df = all_prcp_data_start_end_date_df.loc[all_prcp_data_df["date"]< end]

    min_temp = all_prcp_data_start_end_date_df["prcp"].min()
    max_temp = all_prcp_data_start_end_date_df["prcp"].max()

    avag_temp = all_prcp_data_start_end_date_df["prcp"].mean()

    if all_prcp_data_start_end_date_df["prcp"].count() == 0:
        return("Date out of range")  
    else: return(jsonify({"Min Tempture": min_temp, "Max Tempture": max_temp, "Averge Tempture": avag_temp}))





if __name__ == "__main__":
    app.run(debug=True)