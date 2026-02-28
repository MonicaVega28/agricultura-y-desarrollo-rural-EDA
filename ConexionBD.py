import pandas as pd
from sqlalchemy import create_engine, text
import urllib

from dotenv import load_dotenv
import os

# Le indicas el nombre exacto de tu archivo
load_dotenv("AccesoBD.env")


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
print("✅ Conexión exitosa")