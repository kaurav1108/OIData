import requests
import pandas as pd
import json
import time
import sqlalchemy

engine = sqlalchemy.create_engine('mysql+pymysql://test:Telefonica2035@localhost:3306/fnodatabase')

#index=input("Enter index Name:")   # NIFTY
index='BANKNIFTY'   # NIFTY
#expirarydate=input("Enter expirary Date")  #29-Mar-2023
#equity=input("Enter equity Name:")

url_index="https://www.nseindia.com/api/option-chain-indices?symbol="+ index
print(url_index)
headers_index = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-IN,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,hi;q=0.6,mr;q=0.5",
    "cache-control": "no-cache",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}
session = requests.Session()
data_index = session.get(url_index, headers= headers_index) # This is get data from URL and print the same
data = data_index.json()["records"]["data"]
#print(data)
ocdata = []
while True:
    for i in data:
         for j,k in i.items():
             if j=="CE" or j=="PE":
             #if j=="29-Mar-2023":
                 info = k
                 info["instrumentType"] = j
                 ocdata.append(info)
                 #print(ocdata)
    ocdf = pd.DataFrame(ocdata)
    #print(ocdf)
    tablename = 'bankniftyoidata'
    ocdf.columns = [c.strip() for c in ocdf.columns.values.tolist()]
    ocdf.to_sql(name = tablename, con = engine, index=True, if_exists= 'replace')
    time.sleep(10)
