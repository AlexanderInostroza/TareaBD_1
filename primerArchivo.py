from sqlite3 import Cursor
import pyodbc

try:
    conexion = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-LC6S56LJ;DATABASE=Productos;Trusted_Connection=yes;')
    print("Conexion exitosa")
    cursor = conexion.cursor()
    cursor.execute("SELECT @@version;")
    row=cursor.fetchone()
    print(row)
except Exception as ex: 
    print(ex)

