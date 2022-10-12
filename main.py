from sqlite3 import connect
import pyodbc # pip install pyodbc
import re

##########################################################################################
# formato csv:
#   prod_id;    prod_name;  prod_description;   prod_brand; category;   prod_unit_price
#   int         str         str                 str         str         int
##########################################################################################
# Tablas a crear:
#
# Carrito
#   prod_id     prod_name       prod_brand      quantity
#   int         str             str             int
#
# Boleta
#   prod_id     offer           total_value     final_value
#   int         str             int             int
#
# Oferta
#   prod_id     offer
#   int         str
##########################################################################################


# str de conexion
str_de_conexion = "DRIVER={SQL Server};Server=localhost\SQLEXPRESS01;Database=MultiUSM;Trusted_Connection=True;" # Alex
#str_de_conexion = "DRIVER={SQL Server};SERVER=LAPTOP-LC6S56LJ;DATABASE=MultiUSM;Trusted_Connection=yes;" # Edu

def insertar(cursor, nombre_tabla, lista_variables): 
    instruccion = "INSERT INTO "+nombre_tabla+" VALUES ({vars})"
    con_comilla_simple = ["'"+elemento+"'" for elemento in lista_variables]
    cursor.execute(instruccion.format(vars = ", ".join(con_comilla_simple)))
    pass

def existe_tabla(cursor, tabla):
    return cursor.tables(table=tabla, tableType='TABLE').fetchone()


def mostrar_boleta(cursor):
    cursor.execute("SELECT Productos.prod_name, Productos.prod_unit_price, Boleta.total_value FROM Boleta INNER JOIN Productos ON Boleta.prod_id=Productos.prod_id")
    print ("\n--------------------------MultiUSM--------------------------\n")
    i=1
    for prod_name, unit_price, total in list(cursor.fetchall()):
        cantidad = int(total/unit_price)
        linea = " {:<3} x  {:<42} ${:>7}".format(cantidad,prod_name,total)
        print(linea)
        i+=1
    cursor.execute("SELECT SUM(total_value) FROM Boleta")
    subtotal = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(final_value) FROM Boleta")
    total_boleta = cursor.fetchone()[0]
    linea = " {:<49} ${:>7}"
    print("\n")
    print(linea.format("SUBTOTAL",subtotal))
    print(linea.format("DESCUENTO",subtotal-total_boleta))
    print(linea.format("TOTAL",total_boleta))
    print("\n-------------------GRACIAS POR SU COMPRA-------------------\n")


def top5(cursor):
    cursor.execute("SELECT TOP 5 * FROM Productos ORDER BY prod_unit_price DESC")
    print ("\n######### TOP 5 PRODUCTOS MAS CAROS ########")
    for fila in list(cursor.fetchall()):
        print (fila)




def main():
    connection = pyodbc.connect(str_de_conexion)
    cursor = connection.cursor()   

    if not existe_tabla(cursor, "Productos"):
        cursor.execute("CREATE TABLE Productos (prod_id bigint, prod_name VARCHAR(150), prod_description VARCHAR(150), prod_brand VARCHAR(150), category VARCHAR(150), prod_unit_price int)")
        cursor.execute("CREATE TABLE Carrito (prod_id bigint, prod_name VARCHAR(150), prod_brand VARCHAR(150), quantity int)")
        cursor.execute("CREATE TABLE Boleta (prod_id bigint, offer VARCHAR(150), total_value int, final_value int)")
        cursor.execute("CREATE TABLE Oferta (prod_id bigint, offer VARCHAR(150))")
        ##### LECTURA DEL ARCHIVO Y POBLACION DE TABLAS #####
        re_oferta = re.compile(r".*pag(a|ue) (\d+) *llev(a|e) (\d+).?\n?$")
        archivo_productos = open("ProductosVF2.csv", "r", encoding="UTF-8")
        flag = False
        for linea in archivo_productos:
            if flag:
                lista_variables = linea.replace("'","").strip().split(";")
                prod_id, _, prod_description, _, _, _ = lista_variables
                offerMatch = re_oferta.match(prod_description.lower())
                if offerMatch != None: # Hay oferta
                    offer = offerMatch.group(2) + "x" + offerMatch.group(4)
                    insertar(cursor, "Oferta", [prod_id, offer])
                insertar(cursor, "Productos", lista_variables)
            flag = True
        archivo_productos.close()   
        connection.commit()
    
    print("categoria?")
    categoria = input()
    plantilla_view = "CREATE VIEW category_view AS SELECT prod_id, prod_name, category, prod_unit_price FROM Productos WHERE category='{}'"
    cursor.execute(plantilla_view.format(categoria))
    connection.commit()
    cursor.execute("SELECT * FROM category_view")
    res = cursor.fetchall()
    resultado = list(res)
    for fila in resultado:
        print(fila)
    cursor.execute("SELECT TOP 5 prod_id, prod_name, category, prod_unit_price FROM Productos WHERE category = '{}' ORDER BY prod_unit_price DESC".format(categoria))
    res = cursor.fetchall()
    resultado = list(res)
    print(" #################### TOP 20 ######################")
    for fila in resultado:
        print(fila)
    
    top5(cursor)
    
    # 7707313090775;Tomillo Granaroma ;Tomillo Granaroma x 16 gr;GRANAROMA;Despensa;3690
    # 7707313090812;Canela Granaroma ;Canela Granaroma x 10 gr;GRANAROMA;Despensa;3180
    # 7707313090867;Anís estrellado  Granaroma ;Anís estrellado  Granaroma x 16 gr;GRANAROMA;Despensa;3290
    # 7707313091062;Laurel Granaroma ;Laurel Granaroma x 10 gr;GRANAROMA;Despensa;3260
    # INSERCION DE PRUEBA
    insertar(cursor,"Boleta",["7707313090775","prueba_offer","7380","5000"])
    insertar(cursor,"Boleta",["7707313090812","prueba_offer","3180","3180"])
    insertar(cursor,"Boleta",["7707313090867","prueba_offer","3290","3290"])
    insertar(cursor,"Boleta",["7707313091062","prueba_offer","3260","3260"])
    connection.commit()
    # IMPRIMIR LA BOLETA
    mostrar_boleta(cursor)



if __name__ == "__main__":
    main()