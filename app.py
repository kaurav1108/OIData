from flask import Flask, render_template
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

app = Flask(__name__)

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
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 16900 AND 17600
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
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 39000 AND 41000
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
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 16900 AND 17600
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
WHERE expiryDate = '16-Mar-2023' AND (instrumentType = 'CE' OR instrumentType = 'PE') AND strikePrice between 39000 AND 41000
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
    'pool_size': 14,
    'pool_reset_session': True
}

pool = MySQLConnectionPool(**config)


#cursor = cnx.cursor()

@app.route('/')
def index():
    # execute first query and fetch results
    return render_template('indexold.html')

@app.route("/page1")
def page1():

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

    return render_template('index.html', niftyunderlying=niftyunderlying, niftypcr=niftypcr, bankniftypcr=bankniftypcr, bniftyunderlying=bniftyunderlying, niftyoi=niftyoi, bniftyoi=bniftyoi, breakniftyoi=breakniftyoi, breakbniftyoi=breakbniftyoi)

@app.route("/page2")
def page2():

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
    
    return render_template('index2.html', rangeniftyunderlying=rangeniftyunderlying, rangeniftypcr=rangeniftypcr, rangebankniftypcr=rangebankniftypcr, rangebniftyunderlying=rangebniftyunderlying, rangeniftyoi=rangeniftyoi, rangebniftyoi=rangebniftyoi, rangebreakniftyoi=rangebreakniftyoi, rangebreakbniftyoi=rangebreakbniftyoi)

if __name__ == '__main__':
    app.run()