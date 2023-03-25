import http.client
import json
import hashlib
from datetime import datetime
import sqlalchemy
import pandas as pd
import base64

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

engine = sqlalchemy.create_engine('mysql+pymysql://test:Telefonica2035@localhost:3306/fnodatabase')

# Define the MySQL query
query = "select API_Session from fnodatabase.sessioninfo;"

# Fetch the data into a pandas DataFrame
data = pd.read_sql(query, engine)

# Use the fetched data in your code
#print(data.head())

# Extract the session_token value from the DataFrame
token = data['API_Session'][0]
print(token)

api_key='3354Z73sH2516U9e`_197(4412301228'
api_secret='55875123iF15K6@OI9w2677b651`k439'
#session_token='6773950'
session_token=token
encoded = base64.b64encode(session_token.encode('utf-8'))
base64token = encoded.decode('utf-8')
print(base64token)

# App related Secret Key
secret_key = '55875123iF15K6@OI9w2677b651`k439'

# here is the example of payload
payload = json.dumps({
    "stock_code": "NIFTY",
    "exchange_code": "NFO",
    "expiry_date": "2023-03-29T16:00:00.000Z",
    "product_type": "futures",
    "right": "others",
    "strike_price": "0"
})

#checksum computation
#time_stamp & checksum generation for request-headers
time_stamp = datetime.utcnow().isoformat()[:19] + '.000Z'
checksum = hashlib.sha256((time_stamp+payload+secret_key).encode("utf-8")).hexdigest()

headers = {
    'Content-Type': 'application/json',
    'X-Checksum': 'token '+checksum,
    'X-Timestamp': time_stamp,
    'X-AppKey': api_key,
    'X-SessionToken': base64token #we can get this value from customerdetail call
}

conn = http.client.HTTPSConnection("api.icicidirect.com")
conn.request("GET", "/breezeapi/api/v1/OptionChain", payload, headers)
res = conn.getresponse()
data = res.read()
print(data)
print(data.decode("utf-8"))