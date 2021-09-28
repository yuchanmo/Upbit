from sqlalchemy import create_engine 
coninfo = {
    'user':'sa',
    'pwd':'1',
    'host':'YUNARAUM',
    'database':'CoinStar'
}
sqlserver = create_engine(f"mssql+pymssql://{coninfo['user']}:{coninfo['pwd']}@{coninfo['host']}/{coninfo['database']}", echo=False)
