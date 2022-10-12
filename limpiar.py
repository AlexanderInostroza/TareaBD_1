import pyodbc # pip install pyodbc
import re

# str de conexion
str_de_conexion = "DRIVER={SQL Server};Server=localhost\SQLEXPRESS01;Database=MultiUSM;Trusted_Connection=True;" # Alex
#str_de_conexion = "DRIVER={SQL Server};SERVER=LAPTOP-LC6S56LJ;DATABASE=MultiUSM;Trusted_Connection=yes;" # Edu

connection = pyodbc.connect(str_de_conexion)
cursor = connection.cursor()

cursor.execute("DROP TABLE Productos")
cursor.execute("DROP TABLE Carrito")
cursor.execute("DROP TABLE Boleta")
cursor.execute("DROP TABLE Oferta")
cursor.execute("DROP VIEW category_view")







connection.commit()