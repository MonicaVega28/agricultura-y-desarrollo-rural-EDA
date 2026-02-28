import pandas as pd
from dotenv import load_dotenv
import pyodbc
import os

def get_Tabla(nombre_tabla):
    
    load_dotenv("AccesoBD.env")

    servidor      = os.getenv("servidor")
    base_de_datos = os.getenv("base_de_datos")
    usuario       = os.getenv("usuario")
    contraseña    = os.getenv("contraseña")
   
    
    conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={servidor};"
    f"DATABASE={base_de_datos};"
    f"UID={usuario};"
    f"PWD={contraseña};"
)


    df = pd.read_sql(f"SELECT  * FROM dbo.{nombre_tabla}", conn)
    return df
