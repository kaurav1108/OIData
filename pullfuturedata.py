from breeze_connect import BreezeConnect
import pandas as pd
import sqlalchemy

pd.set_option('display.max_columns', None)

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
# Initialize SDK
breeze = BreezeConnect(api_key=api_key)

# Obtain your session key from https://api.icicidirect.com/apiuser/login?api_key=YOUR_API_KEY
# Incase your api-key has special characters(like +,=,!) then encode the api key before using in the url as shown below.
import urllib
print("https://api.icicidirect.com/apiuser/login?api_key="+urllib.parse.quote_plus(api_key))

# Generate Session
breeze.generate_session(api_secret=api_secret,
                        session_token=session_token)

# Connect to websocket
breeze.ws_connect()

# Callback to receive ticks.
def on_ticks(ticks):
    print("Ticks: {}".format(ticks))

# Assign the callbacks.
breeze.on_ticks = on_ticks

res = breeze.get_historical_data(interval="1minute",
                             from_date= "2023-03-24T07:00:00.000Z",
                             to_date= "2023-03-24T16:00:00.000Z",
                             stock_code="ICIBAN",
                             exchange_code="NFO",
                             product_type="futures",
                             expiry_date="2023-03-29T07:00:00.000Z",
                             right="others",
                             strike_price="0")             
#output = pd.DataFrame(res)   
#print(type(res))

# extract the list of dictionaries from the 'Success' key
data = res['Success']

# create pandas dataframe
df = pd.DataFrame(data)

# print the resulting dataframe
print(df)
