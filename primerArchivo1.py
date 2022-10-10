import pyodbc # pip install pyodbc

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


# lista tipos: True si es tipo int, False si no.
productos_tipos = [True, False, False, False, False, True]
carrito_tipos = [True, False, False, True]
boleta_tipos = [True, False, True, True]
oferta_tipos = [True, False]

def reset():
    return False

def insertar(cursor, nombre_tabla, lista_variables): 
    instruccion = "INSERT INTO "+nombre_tabla+" VALUES ({vars})"
    con_comilla_simple = ["'"+elemento+"'" for elemento in lista_variables]
    print(instruccion.format(vars = ", ".join(con_comilla_simple)))
    cursor.execute(instruccion.format(vars = ", ".join(con_comilla_simple)))
    pass

def existe_tabla(cursor, tabla):
    return cursor.tables(table=tabla, tableType='TABLE').fetchone()

def main():
    

    connection = pyodbc.connect("DRIVER={SQL Server};Server=localhost\SQLEXPRESS01;Database=Tarea1;Trusted_Connection=True;")
    cursor = connection.cursor()

    if existe_tabla(cursor,"notas"): #existe la tabla
        print("exists")
    else:
        print("doesn't exist")
        cursor.execute("CREATE TABLE notas (Nombre VARCHAR(150), Apellido VARCHAR(150), Nota int)") #se crea una tabla
   

    if not cursor.tables(table='Carrito', tableType='TABLE').fetchone(): #existe la tabla
        cursor.execute("CREATE TABLE Productos (prod_id int, prod_name VARCHAR(128), prod_description VARCHAR(128), prod_brand VARCHAR(128), category VARCHAR(128), prod_unit_price int)")

    if not cursor.tables(table='Carrito', tableType='TABLE').fetchone(): #existe la tabla
        cursor.execute("CREATE TABLE Carrito (prod_id int, prod_name VARCHAR(128), prod_brand VARCHAR(128), quantity int)")
    if not cursor.tables(table='Boleta', tableType='TABLE').fetchone(): #existe la tabla
        cursor.execute("CREATE TABLE Boleta (prod_id int, offer VARCHAR(128), total_value int, final_value int)")
    if not cursor.tables(table='Oferta', tableType='TABLE').fetchone(): #existe la tabla
        cursor.execute("CREATE TABLE Oferta (prod_id int, offer VARCHAR(128))")

    archivo_productos = open("ProductosVF2.csv","r")

    flag = False

    for linea in archivo_productos:
        if flag:
            lista_variables = linea.replace("'","").strip().split(";")
            insertar(cursor, "Productos", lista_variables)
        
        flag = True

    if reset():
        pass
        # eliminar tablas
    
    
    connection.commit()


    archivo_productos.close()  
    
    


if __name__ == "__main__":
    main()