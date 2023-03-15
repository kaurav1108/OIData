from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
import pandas as pd

#app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

niftyunderlyingsql="""
select underlying,expiryDate,underlyingValue  FROM fnodatabase.niftyoidata WHERE expiryDate = '16-Mar-2023' LIMIT 1;
"""
bniftyunderlyingsql="""
select underlying,expiryDate,underlyingValue  FROM fnodatabase.bankniftyoidata WHERE expiryDate = '16-Mar-2023' LIMIT 1;
"""
niftyoisql="""
Select 
	CASE
	WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallBuy-PutSell'
    END AS 'CE_Signal',
  MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) AS 'CE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END) AS 'CE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) AS 'CE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END) AS 'CE_Change',
  strikePrice,
  MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END) AS 'PE_Change',
  MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END) AS 'PE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END) AS 'PE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'PE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest',
  CASE
	WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallSell-Putbuy'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallSell-Putbuy'
    END AS 'PE_Signal'
FROM fnodatabase.niftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
GROUP BY strikePrice
ORDER BY strikePrice;
"""
bniftyoisql="""
Select 
	CASE
	WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallBuy-PutSell'
    END AS 'CE_Signal',
  MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) AS 'CE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END) AS 'CE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) AS 'CE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END) AS 'CE_Change',
  strikePrice,
  MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END) AS 'PE_Change',
  MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END) AS 'PE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END) AS 'PE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'PE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest',
  CASE
	WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallSell-Putbuy'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallSell-Putbuy'
    END AS 'PE_Signal'
FROM fnodatabase.bankniftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
GROUP BY strikePrice
ORDER BY strikePrice;
"""
breakniftyoisql="""
select 
round(MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) - MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END),2) AS 'BreakIV',
MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'BreakOI',
MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'BreakCOI',
strikePrice,
  CASE
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
  END AS 'CNT',
    ROUND(MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'CCOIBYNT',
  CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
   END AS 'PNT',
    ROUND(MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'PCOIBYNT'
   FROM fnodatabase.niftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
GROUP BY strikePrice
ORDER BY strikePrice;
"""
breakbniftyoisql="""
select 
round(MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) - MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END),2) AS 'BreakIV',
MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'BreakOI',
MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'BreakCOI',
strikePrice,
  CASE
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
  END AS 'CNT',
    ROUND(MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'CCOIBYNT',
  CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
   END AS 'PNT',
    ROUND(MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'PCOIBYNT'
   FROM fnodatabase.bankniftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
GROUP BY strikePrice
ORDER BY strikePrice;
"""
niftypcrsql = """
SELECT 
    SUM(CE_OpenInterest) AS 'CE_OpenInterest',
    SUM(PE_OpenInterest) AS 'PE_OpenInterest',
    round(SUM(PE_OpenInterest) / SUM(CE_OpenInterest), 2) AS 'PCR'
FROM (
    SELECT 
        MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
        MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest'
    FROM fnodatabase.niftyoidata WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
) subquery;
"""
bankniftypcrsql = """
SELECT 
    SUM(CE_OpenInterest) AS 'CE_OpenInterest',
    SUM(PE_OpenInterest) AS 'PE_OpenInterest',
    round(SUM(PE_OpenInterest) / SUM(CE_OpenInterest), 2) AS 'PCR'
FROM (
    SELECT 
        MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
        MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest'
    FROM fnodatabase.bankniftyoidata WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
) subquery;
"""

rangeniftyunderlyingsql="""
select underlying,expiryDate,underlyingValue  FROM fnodatabase.niftyoidata WHERE expiryDate = '16-Mar-2023' LIMIT 1;
"""
rangebniftyunderlyingsql="""
select underlying,expiryDate,underlyingValue  FROM fnodatabase.bankniftyoidata WHERE expiryDate = '16-Mar-2023' LIMIT 1;
"""
rangeniftyoisql="""
Select 
	CASE
	WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallBuy-PutSell'
    END AS 'CE_Signal',
  MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) AS 'CE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END) AS 'CE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) AS 'CE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END) AS 'CE_Change',
  strikePrice,
  MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END) AS 'PE_Change',
  MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END) AS 'PE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END) AS 'PE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'PE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest',
  CASE
WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallSell-Putbuy'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallSell-Putbuy'
        END AS 'PE_Signal'
FROM fnodatabase.niftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 16600 AND 17600
GROUP BY strikePrice
ORDER BY strikePrice;
"""
rangebniftyoisql="""
Select 
	CASE
	WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallSell-PutBuy'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallBuy-PutSell'
    END AS 'CE_Signal',
  MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) AS 'CE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END) AS 'CE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) AS 'CE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'CE' THEN round(`change`,3) END) AS 'CE_Change',
  strikePrice,
  MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END) AS 'PE_Change',
  MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END) AS 'PE_ImpliedVolatility',
  MAX(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END) AS 'PE_TotalTradedVolume',
  MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'PE_ChangeinOpenInterest',
  MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest',
  CASE
	WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Long Liquidation-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) < 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Short Buildup-CallBuy-PutSell'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) > 0 THEN 'Long Buildup-CallSell-Putbuy'
    WHEN (MAX(CASE WHEN instrumentType = 'PE' THEN round(`change`,3) END)) > 0 AND (MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END)) < 0 THEN 'Short covering-CallSell-Putbuy'
    END AS 'PE_Signal'
FROM fnodatabase.bankniftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 38000 AND 40000
GROUP BY strikePrice
ORDER BY strikePrice;
"""
rangebreakniftyoisql="""
select 
round(MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) - MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END),2) AS 'BreakIV',
MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'BreakOI',
MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'BreakCOI',
strikePrice,
  CASE
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
  END AS 'CNT',
    ROUND(MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'CCOIBYNT',
  CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
   END AS 'PNT',
    ROUND(MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'PCOIBYNT'
   FROM fnodatabase.niftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 16600 AND 17600
GROUP BY strikePrice
ORDER BY strikePrice;
"""
rangebreakbniftyoisql="""
select 
round(MAX(CASE WHEN instrumentType = 'CE' THEN impliedVolatility END) - MAX(CASE WHEN instrumentType = 'PE' THEN impliedVolatility END),2) AS 'BreakIV',
MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'BreakOI',
MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) - MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) AS 'BreakCOI',
strikePrice,
  CASE
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
  END AS 'CNT',
    ROUND(MAX(CASE WHEN instrumentType = 'CE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'CE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'CCOIBYNT',
  CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0'
   END AS 'PNT',
    ROUND(MAX(CASE WHEN instrumentType = 'PE' THEN changeinOpenInterest END) / 
   CASE
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 9 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 4)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 8 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 3)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 7 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 2)))
	WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 6 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    WHEN MAX(LENGTH(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END)) = 5 THEN (MAX(LEFT(CASE WHEN instrumentType = 'PE' THEN (totalTradedVolume*50) END, 1)))
    ELSE '0' END) AS 'PCOIBYNT'
   FROM fnodatabase.bankniftyoidata
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 38000 AND 40000
GROUP BY strikePrice
ORDER BY strikePrice;
"""
rangeniftypcrsql = """
SELECT 
    SUM(CE_OpenInterest) AS 'CE_OpenInterest',
    SUM(PE_OpenInterest) AS 'PE_OpenInterest',
    round(SUM(PE_OpenInterest) / SUM(CE_OpenInterest), 2) AS 'PCR'
FROM (
    SELECT 
        MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
        MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest'
    FROM fnodatabase.niftyoidata WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
) subquery;
"""
rangebankniftypcrsql = """
SELECT 
    SUM(CE_OpenInterest) AS 'CE_OpenInterest',
    SUM(PE_OpenInterest) AS 'PE_OpenInterest',
    round(SUM(PE_OpenInterest) / SUM(CE_OpenInterest), 2) AS 'PCR'
FROM (
    SELECT 
        MAX(CASE WHEN instrumentType = 'CE' THEN openInterest END) AS 'CE_OpenInterest',
        MAX(CASE WHEN instrumentType = 'PE' THEN openInterest END) AS 'PE_OpenInterest'
    FROM fnodatabase.bankniftyoidata WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE')
) subquery;
"""



# configure MySQL connection
# configure MySQL connection pool
config = {
    'user': 'test',
    'password': 'Telefonica2035',
    'host': 'localhost',
    'port': 3306,
    'database': 'fnodatabase',
    'pool_name': 'fnodatabase_pool',
    'pool_size': 16,
    'pool_reset_session': True
}

pool = MySQLConnectionPool(**config)


#cursor = cnx.cursor()
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'signup' in request.form:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            cnx = pool.get_connection()
            cursor = cnx.cursor()
            # Check if email already exists in database
            cursor.execute('SELECT email FROM loginpage WHERE email = %s', (email,))
            result = cursor.fetchone()
            if result:
                # If email exists, display message and don't insert into database
                error_msg = 'You already have an account!'
                return render_template('home.html', error_msg=error_msg)
            else:
                # If email doesn't exist, insert into database and display success message
                cursor.execute('INSERT INTO loginpage (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
                cnx.commit()
                cnx.close()
                return 'Thank you for signing up!'

        elif 'signin' in request.form:
            email = request.form['email']
            password = request.form['password']
            cnx = pool.get_connection()
            cursor = cnx.cursor()
            cursor.execute('SELECT email,password FROM fnodatabase.loginpage WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            if user is not None:
                # set session variable to indicate user is logged in
                session['logged_in'] = True
                # return 'Welcome, ' + user[1] + '!'
                return redirect(url_for('fulloidata'))
            else:        
                error_msg = 'Invalid email or password.'
                return render_template('home.html', error_msg=error_msg)
    return render_template('home.html')


# @app.route('/')
# def index():
#     # execute first query and fetch results
#     return render_template('home.html')

@app.route("/fulloidata", methods=['GET', 'POST'])
def fulloidata():
    # check if user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        # if not, redirect to login page
        return redirect(url_for('home'))
    # if user is logged in, render the fulloidata template
    else:
        if request.method == 'POST' and 'logout' in request.form:
            session.pop('logged_in', None)
            return redirect(url_for('home'))
        else:
            # get a connection from the pool
            cnx = pool.get_connection()
            cursor = cnx.cursor()

            # execute niftyunderlying query and fetch results
            cursor.execute(niftyunderlyingsql)
            niftyunderlying = cursor.fetchall()

            # execute niftyunderlying query and fetch results
            cursor.execute(niftypcrsql)
            niftypcr = cursor.fetchall()

            # execute bniftyunderlying query and fetch results
            cursor.execute(bniftyunderlyingsql)
            bniftyunderlying = cursor.fetchall()

                # execute bniftyunderlying query and fetch results
            cursor.execute(bankniftypcrsql)
            bankniftypcr = cursor.fetchall()

            # execute niftyoi query and fetch results
            cursor.execute(niftyoisql)
            niftyoi = cursor.fetchall()

            # execute bniftyoi query and fetch results
            cursor.execute(bniftyoisql)
            bniftyoi = cursor.fetchall()

            # execute breakniftyoi query and fetch results
            cursor.execute(breakniftyoisql)
            breakniftyoi = cursor.fetchall()

            # execute breakbniftyoi query and fetch results
            cursor.execute(breakbniftyoisql)
            breakbniftyoi = cursor.fetchall()

            cursor.close()
            cnx.close()

            return render_template('fulloidata.html', niftyunderlying=niftyunderlying, niftypcr=niftypcr, bankniftypcr=bankniftypcr, bniftyunderlying=bniftyunderlying, niftyoi=niftyoi, bniftyoi=bniftyoi, breakniftyoi=breakniftyoi, breakbniftyoi=breakbniftyoi)

@app.route("/rangeoidata")
def rangeoidata():
    if 'logged_in' not in session or not session['logged_in']:
    # if not, redirect to login page
        return redirect(url_for('home'))
    # if user is logged in, render the fulloidata template
    else:

        # get a connection from the pool
        cnx = pool.get_connection()
        cursor = cnx.cursor()

        # execute niftyunderlying query and fetch results
        cursor.execute(rangeniftyunderlyingsql)
        rangeniftyunderlying = cursor.fetchall()

        # execute niftyunderlying query and fetch results
        cursor.execute(rangeniftypcrsql)
        rangeniftypcr = cursor.fetchall()

        # execute bniftyunderlying query and fetch results
        cursor.execute(rangebniftyunderlyingsql)
        rangebniftyunderlying = cursor.fetchall()

            # execute bniftyunderlying query and fetch results
        cursor.execute(rangebankniftypcrsql)
        rangebankniftypcr = cursor.fetchall()

        # execute niftyoi query and fetch results
        cursor.execute(rangeniftyoisql)
        rangeniftyoi = cursor.fetchall()

        # execute bniftyoi query and fetch results
        cursor.execute(rangebniftyoisql)
        rangebniftyoi = cursor.fetchall()

        # execute breakniftyoi query and fetch results
        cursor.execute(rangebreakniftyoisql)
        rangebreakniftyoi = cursor.fetchall()

        # execute breakbniftyoi query and fetch results
        cursor.execute(rangebreakbniftyoisql)
        rangebreakbniftyoi = cursor.fetchall()

        cursor.close()
        cnx.close()

        return render_template('rangeoidata.html', rangeniftyunderlying=rangeniftyunderlying, rangeniftypcr=rangeniftypcr, rangebankniftypcr=rangebankniftypcr, rangebniftyunderlying=rangebniftyunderlying, rangeniftyoi=rangeniftyoi, rangebniftyoi=rangebniftyoi, rangebreakniftyoi=rangebreakniftyoi, rangebreakbniftyoi=rangebreakbniftyoi)

@app.route("/fiidiidata")
def fiidiidata():
    if 'logged_in' not in session or not session['logged_in']:
    # if not, redirect to login page
        return redirect(url_for('home'))
    # if user is logged in, render the fulloidata template
    else:
        fiidiisql = """
            SELECT * FROM fnodatabase.open_interest;
            """
        connection = pool.get_connection()

        # Execute the query and store the results in a Pandas dataframe
        df = pd.read_sql(fiidiisql, con=connection)

        # Close the database connection
        connection.close()

        df['Date'] = df['Date'].dt.date

        # Create separate dataframes for each client type
        df_client = df[df['Client Type'] == 'Client']
        df_dii = df[df['Client Type'] == 'DII']
        df_fii = df[df['Client Type'] == 'FII']
        df_pro = df[df['Client Type'] == 'Pro']

        # Add a new column to each dataframe that contains the difference between Long - Short Difference
        df_client.loc[:, 'Future Long - Short'] = df_client['Future Index Long'] - df_client['Future Index Short']
        df_dii.loc[:, 'Future Long - Short'] = df_dii['Future Index Long'] - df_dii['Future Index Short']
        df_fii.loc[:, 'Future Long - Short'] = df_fii['Future Index Long'] - df_fii['Future Index Short']
        df_pro.loc[:, 'Future Long - Short'] = df_pro['Future Index Long'] - df_pro['Future Index Short']

        # Add a new column to each dataframe that contains the difference between consecutive rows
        df_client.loc[:, 'FROC'] = (df_client['Future Long - Short'].diff()).fillna(0).astype(int)
        df_dii.loc[:, 'FROC'] = (df_dii['Future Long - Short'].diff()).fillna(0).astype(int)
        df_fii.loc[:, 'FROC'] = (df_fii['Future Long - Short'].diff()).fillna(0).astype(int)
        df_pro.loc[:, 'FROC'] = (df_pro['Future Long - Short'].diff()).fillna(0).astype(int)

        # Add a new column that categorizes the 'Difference Between Rows' column as 'Bullish' or 'Bearish'
        df_client.loc[:, 'Future Trend'] = df_client['FROC'].apply(lambda x: 'Bullish' if x > 0 else 'Bearish')
        df_dii.loc[:, 'Future Trend'] = df_dii['FROC'].apply(lambda x: 'Bullish' if x > 0 else 'Bearish')
        df_fii.loc[:, 'Future Trend'] = df_fii['FROC'].apply(lambda x: 'Bullish' if x > 0 else 'Bearish')
        df_pro.loc[:, 'Future Trend'] = df_pro['FROC'].apply(lambda x: 'Bullish' if x > 0 else 'Bearish')


        #Netcall	Call long - short
        df_client.loc[:, 'Call Long - Short'] = df_client['Option Index Call Long'] - df_client['Option Index Call Short']
        df_dii.loc[:, 'Call Long - Short'] = df_dii['Option Index Call Long'] - df_dii['Option Index Call Short']
        df_fii.loc[:, 'Call Long - Short'] = df_fii['Option Index Call Long'] - df_fii['Option Index Call Short']
        df_pro.loc[:, 'Call Long - Short'] = df_pro['Option Index Call Long'] - df_pro['Option Index Call Short']

        #NetPut	    Put long - short
        df_client.loc[:, 'Put Long - Short'] = df_client['Option Index Put Long'] - df_client['Option Index Put Short']
        df_dii.loc[:, 'Put Long - Short'] = df_dii['Option Index Put Long'] - df_dii['Option Index Put Short']
        df_fii.loc[:, 'Put Long - Short'] = df_fii['Option Index Put Long'] - df_fii['Option Index Put Short']
        df_pro.loc[:, 'Put Long - Short'] = df_pro['Option Index Put Long'] - df_pro['Option Index Put Short']

        #Call ROC CD - PD
        df_client.loc[:, 'Call ROC'] = (df_client['Call Long - Short'].diff()).fillna(0).astype(int)
        df_dii.loc[:, 'Call ROC'] = (df_dii['Call Long - Short'].diff()).fillna(0).astype(int)
        df_fii.loc[:, 'Call ROC'] = (df_fii['Call Long - Short'].diff()).fillna(0).astype(int)
        df_pro.loc[:, 'Call ROC'] = (df_pro['Call Long - Short'].diff()).fillna(0).astype(int)

        # Add a new column that categorizes the 'Difference Between Rows' column as 'Bullish' or 'Bearish'
        df_client.loc[:, 'CE Activity'] = df_client['Call ROC'].apply(lambda x: 'Bought-Calls-Bullish' if x > 0 else 'Sold-Calls-Bearish')
        df_dii.loc[:, 'CE Activity'] = df_dii['Call ROC'].apply(lambda x: 'Bought-Calls-Bullish' if x > 0 else 'Sold-Calls-Bearish')
        df_fii.loc[:, 'CE Activity'] = df_fii['Call ROC'].apply(lambda x: 'Bought-Calls-Bullish' if x > 0 else 'Sold-Calls-Bearish')
        df_pro.loc[:, 'CE Activity'] = df_pro['Call ROC'].apply(lambda x: 'Bought-Calls-Bullish' if x > 0 else 'Sold-Calls-Bearish')

        #Put ROC CD - PD
        df_client.loc[:, 'Put ROC'] = (df_client['Put Long - Short'].diff()).fillna(0).astype(int)
        df_dii.loc[:, 'Put ROC'] = (df_dii['Put Long - Short'].diff()).fillna(0).astype(int)
        df_fii.loc[:, 'Put ROC'] = (df_fii['Put Long - Short'].diff()).fillna(0).astype(int)
        df_pro.loc[:, 'Put ROC'] = (df_pro['Put Long - Short'].diff()).fillna(0).astype(int)


        # Add a new column that categorizes the 'Difference Between Rows' column as 'Bullish' or 'Bearish'
        df_client.loc[:, 'PE Activity'] = df_client['Put ROC'].apply(lambda x: 'Bought-Puts-Bearish' if x > 0 else 'Sold-Puts-Bullish')
        df_dii.loc[:, 'PE Activity'] = df_dii['Put ROC'].apply(lambda x: 'Bought-Puts-Bearish' if x > 0 else 'Sold-Puts-Bullish')
        df_fii.loc[:, 'PE Activity'] = df_fii['Put ROC'].apply(lambda x: 'Bought-Puts-Bearish' if x > 0 else 'Sold-Puts-Bullish')
        df_pro.loc[:, 'PE Activity'] = df_pro['Put ROC'].apply(lambda x: 'Bought-Puts-Bearish' if x > 0 else 'Sold-Puts-Bullish')

        # Sort the dataframes in descending order based on the difference column
        df_client = df_client.sort_values(by='Date', ascending=False)
        df_dii = df_dii.sort_values(by='Date', ascending=False)
        df_fii = df_fii.sort_values(by='Date', ascending=False)
        df_pro = df_pro.sort_values(by='Date', ascending=False)


        return render_template('fiidiidata.html', df_client=df_client, df_dii=df_dii, df_fii=df_fii, df_pro=df_pro)

if __name__ == '__main__':
    app.run()

 
    