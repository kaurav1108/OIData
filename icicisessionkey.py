from breeze_connect import BreezeConnect
import http.client
import json
import sqlalchemy
import pandas as pd

engine = sqlalchemy.create_engine('mysql+pymysql://test:Telefonica2035@localhost:3306/fnodatabase')

conn = http.client.HTTPSConnection('api.icicidirect.com')

payload = "{\r\n    \"password\": \"Munich$2033\",\r\n   \"dOB\": \"08051991\",\r\n    "\
            "\"ip_ID\": \"127.0.0.1\",\r\n    \"appkey\": \"3354Z73sH2516U9e`_197(4412301228\",\r\n    "\
            "\"idirect_Userid\": \"lucky8591\",  \r\n    \"user_data\": \"ALL\"\r\n}"
headers = {"Content-Type":"application/json"}
conn.request("GET", "/breezeapi/api/v1/customerlogin", payload, headers)
res = conn.getresponse()
data = json.loads((res.read()).decode("utf-8"))
#print(data)
#print(type(data))

# extract the inner dictionary and convert it to a list of dictionaries
inner_data = data['Success']
list_of_dicts = [inner_data]

# create a Pandas DataFrame from the list of dictionaries
df = pd.DataFrame(list_of_dicts, columns=['API_Session', 'user_id', 'prioritycustflg', 'cust_id', 'mobile_no'])
#print(df)

# specify column data types for MySQL table
dtypes = {'API_Session': sqlalchemy.types.String(length=10),
          'user_id': sqlalchemy.types.String(length=20),
          'prioritycustflg': sqlalchemy.types.String(length=1),
          'cust_id': sqlalchemy.types.String(length=15),
          'mobile_no': sqlalchemy.types.String(length=10)}

# insert data into MySQL table
tablename = 'sessioninfo'

with engine.connect() as conn:
    transaction = conn.begin()
    try:
        df.to_sql(name=tablename, con=conn, index=False, if_exists='replace', dtype=dtypes)
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        print(f"Error inserting data: {e}")
        raise

# dispose of the database connection
engine.dispose()
print("Done")




