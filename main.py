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
#str_de_conexion = "DRIVER={SQL Server};Server=localhost\SQLEXPRESS01;Database=MultiUSM;Trusted_Connection=True;" # Alex
str_de_conexion = "DRIVER={SQL Server};SERVER=LAPTOP-LC6S56LJ;DATABASE=MultiUSM;Trusted_Connection=yes;" # Edu

'''
Descripcion de la funcion

    Parametros:
        a (int): Descripcion del parametro a
        b (int): Descripcion del parametro b

    Retorno:
        c (str): Descripcion del parametro c
'''

def top5(cursor):
    '''
    Muestra por pantalla los 5 productos más caros.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
    '''
    cursor.execute("SELECT TOP 5 * FROM Productos ORDER BY prod_unit_price DESC")
    print ("\n############# TOP 5 PRODUCTOS MAS CAROS #############")
    for _, prod_name, prod_description, _, _, prod_unit_price in list(cursor.fetchall()):
        print("------------------------------")
        print("Nombre: " + prod_name)
        print("Descripción: " + prod_description)
        print("Precio: " + str(prod_unit_price))
        print("------------------------------")

def top5_por_categoria(cursor,categoria):
    '''
    Muestra por pantalla los 5 productos más caros de la categoría.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
            categoria (str): Nombre de la categoría.
    '''
    categoria_formateada = categoria.replace(" ","_").replace(",","_")
    cursor.execute("SELECT TOP 5 * FROM {} ORDER BY prod_unit_price DESC".format(categoria_formateada))
    print ("\n############# TOP 5 PRODUCTOS MAS CAROS EN LA CATEGORIA {} #############".format(categoria_formateada.upper()))
    for prod_name, prod_description, prod_unit_price in list(cursor.fetchall()):
        print("------------------------------")
        print("Nombre: " + prod_name)
        print("Descripción: " + prod_description)
        print("Precio: " + str(prod_unit_price))
        print("------------------------------")

def agregar_al_carrito(cursor, prod_id, cantidad):
    '''
    Agrega un producto al carro de compras.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
            prod_id (int): ID del producto.
            cantidad (int): Cantidad de producto.
    '''
    cursor.execute("SELECT * FROM Carrito WHERE prod_id={}".format(prod_id))
    match = list(cursor.fetchall())
    if len(match) > 0: # Ya estaba en la tabla
        _, _, _, quantity = match[0]
        cursor.execute("EXEC PR_Cambiar_cantidad {},{},{}".format(quantity,cantidad,prod_id))
    else:
        cursor.execute("SELECT * FROM Productos WHERE prod_id={}".format(prod_id))
        filas_Productos = list(cursor.fetchall())
        _, prod_name, _, prod_brand, _, _ =  filas_Productos[0]
        insertar(cursor, "Carrito", [str(prod_id), prod_name, prod_brand, str(cantidad)])

def mostrar_carrito(cursor):
    '''
    Muestra los productos del carrito por pantalla.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
    '''
    cursor.execute("SELECT Carrito.prod_name, Carrito.quantity, Productos.prod_unit_price FROM Carrito INNER JOIN Productos ON Carrito.prod_id=Productos.prod_id")
    res = list(cursor.fetchall())
    if len(res) == 0:
        print("Carrito Vacio")
        return
    print("################## ACTUALMENTE EN EL CARRITO ##################")
    for prod_name, quantity, prod_unit_price in res:
        print(" {:>3} x  {:<42} ${:>7} c/u".format(quantity, prod_name, prod_unit_price))

def insertar(cursor, nombre_tabla, lista_variables): 
    '''
    Inserta una fila en una tabla.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
            nombre_tabla (str): Tabla en la que se insertarán los datos.
            lista_variables (lista): Lista de strings con la información que se quiere agregar. Debe respetar el formato de la tabla.
    ''' 
    instruccion = "INSERT INTO "+nombre_tabla+" VALUES ({vars})"
    con_comilla_simple = ["'"+elemento+"'" for elemento in lista_variables]
    cursor.execute(instruccion.format(vars = ", ".join(con_comilla_simple)))

def crear_views(cursor, lista_categorias):
    '''
    Crea una view por cada categoría.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
            lista_categorias (lista): Lista con las categorías como strings. 
    '''
    for categoria in lista_categorias:
        instruccion = "CREATE VIEW "+ categoria.replace(" ","_").replace(",","_")+ " as SELECT prod_name,prod_description,prod_unit_price FROM Productos WHERE category='" + categoria + "'"
        cursor.execute(instruccion)

def existe_tabla(cursor, tabla):
    '''
    Determina si existe una tabla en la base de datos.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
            tabla (str): Nombre de la tabla.
        Retorno:
            (bool): True si existe la tabla, False si no.
    '''
    return cursor.tables(table=tabla, tableType='TABLE').fetchone()

# CASO COMPLICADO: Lavaloza Fab loza max  citrus liquido repuesto 
def buscar_producto(cursor, nombre_producto):
    '''
    Busca los productos con el nombre indicado.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
            nombre_producto (str): Nombre del producto.

        Retorno:
            (lista): En la primera posición, un booleano (True si se encontró el producto, False si no) 
            y en cada posición subsiguiente, un ID por cada producto con el nombre solicitado.
    '''
    cursor.execute("SELECT * FROM Productos WHERE prod_name='"+ nombre_producto +"'")
    prod_encontrado = cursor.fetchall()
    if len(prod_encontrado) > 0:
        retorno = [True]
        for prod_id, prod_name, prod_description, prod_brand, category, prod_unit_price in prod_encontrado:
            print("--------------------------------------------------------------------------------------")
            print("ID del producto: {}".format(prod_id))
            print("Nombre: {}".format(prod_name))
            print("Descripción: {}".format(prod_description))
            print("Marca: {}".format(prod_brand))
            print("Categoría: {}".format(category))
            print("Precio: {}".format(prod_unit_price))
            print("--------------------------------------------------------------------------------------")
            retorno.append(str(prod_id))
        return retorno
    return [False]

def generar_boleta(cursor):
    '''
    Genera la boleta.

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
    '''
    ofertas = {}
    cursor.execute("DELETE FROM Boleta")
    cursor.execute("SELECT Carrito.prod_id, Oferta.offer FROM Oferta INNER JOIN Carrito ON Carrito.prod_id=Oferta.prod_id")
    for prod_id, offer in list(cursor.fetchall()):
        M,N = offer.split("x")
        ofertas[prod_id] = (int(M),int(N))
    cursor.execute("SELECT Carrito.prod_id, Carrito.quantity, Productos.prod_unit_price FROM Carrito INNER JOIN Productos ON Carrito.prod_id=Productos.prod_id")
    for prod_id, quantity, unit_price in list(cursor.fetchall()):
        total_value = quantity * unit_price
        final_value = total_value
        offer = ""
        if prod_id in ofertas:
            M,N = ofertas[prod_id]
            fuera_de_oferta = quantity % N
            con_oferta = (quantity // N) * M
            final_value = (con_oferta + fuera_de_oferta) * unit_price
            offer = str(M)+"x"+str(N)
        insertar(cursor, "Boleta", [str(prod_id), offer, str(total_value), str(final_value)])

def mostrar_boleta(cursor):
    '''
    Muestra la boleta por pantalla

        Parametros:
            cursor (Cursor de pyodbc): Cursor de conección.
    '''
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

def main():
    connection = pyodbc.connect(str_de_conexion)
    cursor = connection.cursor()   
    #categorias = list()
    primera_ejecucion = False
    if not existe_tabla(cursor, "Productos"):
        primera_ejecucion = True
        cursor.execute("CREATE TABLE Productos (prod_id bigint, prod_name VARCHAR(150), prod_description VARCHAR(150), prod_brand VARCHAR(150), category VARCHAR(150), prod_unit_price int)")
        cursor.execute("CREATE TABLE Carrito (prod_id bigint, prod_name VARCHAR(150), prod_brand VARCHAR(150), quantity int)")
        cursor.execute("CREATE TABLE Boleta (prod_id bigint, offer VARCHAR(150), total_value int, final_value int)")
        cursor.execute("CREATE TABLE Oferta (prod_id bigint, offer VARCHAR(150))")
        cursor.execute("CREATE PROCEDURE PR_Cambiar_cantidad @Cantidad_actual as int,@Cantidad_cambio as int, @id_prod as bigint AS BEGIN DECLARE @Final_cantidad int SET @Final_cantidad = [dbo].[Valor_cantidad] (@Cantidad_actual,@Cantidad_cambio) UPDATE Carrito SET quantity=@Final_cantidad WHERE prod_id=@id_prod END")
        cursor.execute("CREATE TRIGGER TR_Productos_Eliminados on Carrito FOR UPDATE as BEGIN DELETE FROM Carrito WHERE quantity=0 END")
        cursor.execute("CREATE FUNCTION Valor_cantidad (@Cantidad_actual int,@Variacion_cantidad int)RETURNS int as BEGIN DECLARE @Cantidad_final int SET @Cantidad_final = @Cantidad_actual + @Variacion_cantidad IF @Cantidad_final < 0 RETURN 0 RETURN @Cantidad_final END")

        archivo_productos = open("ProductosVF2.csv","r",encoding="UTF-8")
        flag = False
        re_oferta = re.compile(r".*pag(a|ue) (\d+) *llev(a|e) (\d+).?\n?$")
        for linea in archivo_productos:
            if flag:
                lista_variables = linea.replace("'","").strip().split(";")
                prod_id, _, prod_description, _, category, _ = lista_variables
                insertar(cursor, "Productos", lista_variables)
                offerMatch = re_oferta.match(prod_description.lower())
                if offerMatch != None:
                    offer = offerMatch.group(2) + "x" + offerMatch.group(4)
                    insertar(cursor, "Oferta", [prod_id, offer])
            flag = True
        archivo_productos.close() 

    cursor.execute("SELECT DISTINCT category FROM Productos")
    categorias = [tup[0] for tup in list(cursor.fetchall())]
    if primera_ejecucion:
        crear_views(cursor,categorias)

    connection.commit()
        
    opcion = 1
    while opcion != 7:
        print("\n#################### MENÚ ####################")
        print("1. Buscar producto")
        print("2. Ver los 5 productos mas caros")
        print("3. Ver Categorias")
        print("4. Mostrar mi carrito")
        print("5. Eliminar un elemento de mi carrito")
        print("6. Limpiar mi carrito")
        print("7. Finalizar compras")
        opcion = int(input("Ingrese un numero: "))
        print("")

        if opcion == 1:
            prod_buscado = input("Ingrese el nombre del producto: ")
            busqueda = buscar_producto(cursor,prod_buscado)
            if busqueda[0]:
                if len(busqueda) == 2:
                    agregar = input("Desea agregar el producto al carrito? (y/n): ")
                    if agregar.lower() == "y":
                        cantidad = int(input("Cuantas unidades desea agregar?: "))
                        agregar_al_carrito(cursor,busqueda[1],cantidad)
                        connection.commit()
                        print("Producto agregado correctamente")
                    else:
                        print("Producto no agregado")
                else:
                    agregar = input("Si desea agregar uno de estos productos al carrito, escriba el ID del producto: ")
                    if agregar in busqueda[1:]:
                        cantidad = int(input("Cuantas unidades desea agregar?: "))
                        agregar_al_carrito(cursor, agregar, cantidad)
                        connection.commit()
                        print("Producto agregado correctamente")
                    else:
                        print("Producto no encontrado")
            else:
                print("Producto no encontrado")

        elif opcion == 2:
            top5(cursor)

        elif opcion == 3:
            opcion_categoria = 0
            while opcion_categoria != len(categorias):
                print("Categorias disponibles:")
                contador = 0
                linea_categoria = "{:>2}. {}"
                for categoria in categorias:
                    print(linea_categoria.format(contador+1,categoria))
                    contador+=1
                print(linea_categoria.format(contador+1,"Volver"))
                opcion_categoria = (int(input("Ingrese un numero: "))) - 1

                if opcion_categoria < 0 or opcion_categoria > len(categorias):
                    print("\nOpcion invalida, reintente:")

                if opcion_categoria >= 0 and opcion_categoria < len(categorias):
                    ver_top5 = input("Desea ver solo los 5 productos mas caros? (y/n): ")
                    if ver_top5 == "y":
                        top5_por_categoria(cursor,categorias[opcion_categoria])
                    else:
                        cursor.execute("SELECT * FROM " + categorias[opcion_categoria].replace(" ","_").replace(",","_"))
                        prods = cursor.fetchall()
                        for prod in prods:
                            print("--------------------------------------------------------------------------------------")
                            print("Nombre: " + prod[0])
                            print("Descripción: " + prod[1])
                            print("Precio: " + str(prod[2]))
                            print("--------------------------------------------------------------------------------------")

        elif opcion == 4:
            mostrar_carrito(cursor)

        elif opcion == 5:
            cursor.execute("SELECT * FROM Carrito")
            prod_encontrado = cursor.fetchall()
            if len(prod_encontrado) > 0:
                for prod in prod_encontrado:
                    print("--------------------------------------------------------------------------------------")
                    print("Codigo: " + str(prod[0]))
                    print("Nombre: " + prod[1])
                    print("Marca: " + prod[2])
                    print("Cantidad: " + str(prod[3]))
                    print("--------------------------------------------------------------------------------------")
                nombre_prod = input("Ingrese el nombre del producto que desea eliminar: ")
                cursor.execute("SELECT * FROM Carrito WHERE prod_name='" + nombre_prod + "'")
                prods_encontrados = cursor.fetchall()
                if len(prods_encontrados) == 1:
                    cantidad = -(int(input("Ingrese las unidades que desea eliminar: ")))
                    prod_id, _, _, quantity = prods_encontrados[0]
                    cursor.execute("EXEC PR_Cambiar_cantidad {},{},{}".format(quantity,cantidad,prod_id))
                elif len(prods_encontrados) > 1:
                    print("Se encontraron varios productos con el mismo nombre")
                    prod_id = input("Escriba el ID del producto que desea eliminar: ")
                    cursor.execute("SELECT * FROM Carrito WHERE prod_id={}".format(prod_id))
                    prod_encontrado = cursor.fetchall()
                    if len(prod_encontrado) == 1:
                        cantidad = -(int(input("Ingrese las unidades que desea eliminar: ")))
                        cursor.execute("EXEC PR_Cambiar_cantidad {},{},{}".format(prod_encontrado[0][3],cantidad,prod_id))
                    else:
                        print("El producto ingresado no existe en el carrito")
                else: 
                    print("El producto ingresado no existe en el carrito")
            else:
                print("Carrito Vacio")

        elif opcion == 6:
            cursor.execute("DELETE FROM Carrito")
            print("Carrito vaciado")

        elif opcion == 7:
            cursor.execute("SELECT * FROM Carrito")
            compras = cursor.fetchall()
            if len(compras) > 0:
                generar_boleta(cursor)
                connection.commit()
                mostrar_boleta(cursor)
            else:
                print ("\n--------------------------MultiUSM--------------------------\n")
                print("No se ha comprado ningun producto")
                print("\n-------------------GRACIAS POR SU COMPRA-------------------\n")
                
            #cursor.execute("DELETE FROM Carrito")

        else:
            print("Opcion invalida, reintente")
            
    connection.commit()
    cursor.close()
    connection.close()

#Jabon Lak sensaciones barra 
if __name__ == "__main__":
    main()