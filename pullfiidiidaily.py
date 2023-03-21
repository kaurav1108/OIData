import pandas as pd
from datetime import datetime
import sqlalchemy
engine = sqlalchemy.create_engine('mysql+pymysql://test:Telefonica2035@localhost:3306/fnodatabase')
isVolDataLoad = False   # set this true for volume data and false for open Interest Data
#url = https://archives.nseindia.com/content/nsccl/fao_participant_oi_20052022.csv
#urlvolume
#dt = pd.date_range(start="02/21/2023", end="02/21/2023", freq='B')   # enter start and end date MDY as per your need MMDDYYY
dt = pd.date_range(start = datetime.today(), end = datetime.today(), freq='B')   # enter start and end date MDY as per your need MMDDYYY
#dt = pd.to_datetime('today').normalize()
#dt =  datetime.today().strftime("%d%m%Y")
#print(dt)

for tday in dt:
    try:
        dmyformat = datetime.strftime(tday, "%d%m%Y")
        #print(dmyformat)
        #dmyformat = datetime.strftime(tday)
        #dmyformat = dt
        url = 'https://www1.nseindia.com/content/nsccl/fao_participant_oi_'+ dmyformat +'.csv'
        print(url)
        tablename = 'open_interest'
        if isVolDataLoad:
            url = 'https://archives.nseindia.com/content/nsccl/fao_participant_vol_'+ dmyformat +'.csv'
            tablename = 'volume1'
        data = pd.read_csv(url,skiprows=1)
        data = data.drop(data.index[4])
        data.insert(0, 'Date', tday)    #insert current Data in first column
        data.columns = [c.strip() for c in data.columns.values.tolist()]
        data.to_sql(name = tablename, con = engine, index = False, if_exists= 'append')
        print("Data Successfully update for " + dmyformat)
    except Exception:
        print("Oops Error in " + dmyformat )
engine.dispose()
print("Done")
