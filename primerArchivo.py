import pyodbc
import pandas as pd
import re

"""
try:
    conexion = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-LC6S56LJ;DATABASE=MultiUSM;Trusted_Connection=yes;')
    print("Conexion exitosa")
    cursor = conexion.cursor()
    cursor.execute("SELECT @@version;")
    row=cursor.fetchone()
    print(row)
except Exception as ex: 
    print(ex)


conexion.close()
"""

datos = pd.read_csv('ProductosVF2.csv', sep=';')
contador = 0
lista_prod = list()
lista_ofertas = list()
for ides in datos["prod_id"]:
    lista_prod.append(list())
    lista_prod[contador].append(str(ides))
    contador+=1
contador = 0

for name in datos["prod_name"]:
    lista_prod[contador].append(name)
    contador+=1
contador = 0

for desc in datos["prod_description"]:
    lista_prod[contador].append(desc)
    contador+=1
contador = 0

for brand in datos["prod_brand"]:
    lista_prod[contador].append(brand)
    contador+=1
contador = 0

for cate in datos["category"]:
    lista_prod[contador].append(cate)
    contador+=1
contador = 0

for unit in datos["prod_unit_price"]:
    lista_prod[contador].append(str(unit))
    contador+=1

print(lista_prod[0])
for producto in lista_prod:
    if (len(re.findall(r"pague [0-9] lleve [0-9]", producto[2])) > 0):
        lista_ofertas.append(producto)
print(len(lista_ofertas))

