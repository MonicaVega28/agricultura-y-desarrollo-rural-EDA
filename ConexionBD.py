import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pyodbc
import urllib
import os

def get_Tabla(nombre_tabla):
    
    load_dotenv("credencialesAcceso.env")

    servidor      = os.getenv("servidor")
    base_de_datos = os.getenv("base_de_datos")
    usuario       = os.getenv("usuario")
    contraseña    = os.getenv("contraseña")


    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={servidor};"
        f"DATABASE={base_de_datos};"
        f"UID={usuario};"
        f"PWD={contraseña};"
    )

    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)



    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT top 10  * FROM dbo.{nombre_tabla}", conn)
    return df
