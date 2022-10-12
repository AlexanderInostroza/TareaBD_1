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



def top5(cursor):
    cursor.execute("SELECT TOP 5 * FROM Productos ORDER BY prod_unit_price DESC")
    print ("\n############# TOP 5 PRODUCTOS MAS CAROS #############")
    for _, prod_name, prod_description, _, _, prod_unit_price in list(cursor.fetchall()):
        print("------------------------------")
        print("Nombre: " + prod_name)
        print("Descripción: " + prod_description)
        print("Precio: " + str(prod_unit_price))
        print("------------------------------")

def top5_por_categoria(cursor,categoria):
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
    cursor.execute("SELECT * FROM Carrito WHERE prod_id={}".format(prod_id))
    match = list(cursor.fetchall())
    if len(match) > 0: # Ya estaba en la tabla
        _, _, _, quantity = match[0]
        cursor.execute("UPDATE Carrito SET quantity={} WHERE prod_id={}".format(cantidad+quantity,prod_id))
    else:
        cursor.execute("SELECT * FROM Productos WHERE prod_id={}".format(prod_id))
        filas_Productos = list(cursor.fetchall())
        _, prod_name, _, prod_brand, _, _ =  filas_Productos[0]
        insertar(cursor, "Carrito", [str(prod_id), prod_name, prod_brand, str(cantidad)])

def insertar(cursor, nombre_tabla, lista_variables): 
    instruccion = "INSERT INTO "+nombre_tabla+" VALUES ({vars})"
    con_comilla_simple = ["'"+elemento+"'" for elemento in lista_variables]
    #print(instruccion.format(vars = ", ".join(con_comilla_simple)))
    cursor.execute(instruccion.format(vars = ", ".join(con_comilla_simple)))
    pass

def crear_views(cursor, lista_categorias):
    for categoria in lista_categorias:
        instruccion = "CREATE VIEW "+ categoria.replace(" ","_").replace(",","_")+ " as SELECT prod_name,prod_description,prod_unit_price FROM Productos WHERE category='" + categoria + "'"
        cursor.execute(instruccion)

def existe_tabla(cursor, tabla):
    return cursor.tables(table=tabla, tableType='TABLE').fetchone()

# CASO COMPLICADO: Lavaloza Fab loza max  citrus liquido repuesto 
def buscar_producto(cursor, nombre_producto):
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

def main():
    connection = pyodbc.connect(str_de_conexion)
    cursor = connection.cursor()   
    archivo_productos = open("ProductosVF2.csv","r",encoding="UTF-8")

    if not existe_tabla(cursor, "Productos"):
        cursor.execute("CREATE TABLE Productos (prod_id bigint, prod_name VARCHAR(150), prod_description VARCHAR(150), prod_brand VARCHAR(150), category VARCHAR(150), prod_unit_price int)")
        cursor.execute("CREATE TABLE Carrito (prod_id bigint, prod_name VARCHAR(150), prod_brand VARCHAR(150), quantity int)")
        cursor.execute("CREATE TABLE Boleta (prod_id bigint, offer VARCHAR(150), total_value int, final_value int)")
        cursor.execute("CREATE TABLE Oferta (prod_id bigint, offer VARCHAR(150))")

        flag = False
        re_oferta = re.compile(r".*pag(a|ue) (\d+) *llev(a|e) (\d+).?\n?$")
        categorias = list()
        for linea in archivo_productos:
            if flag:
                lista_variables = linea.replace("'","").strip().split(";")
                prod_id, _, prod_description, _, category, _ = lista_variables
                insertar(cursor, "Productos", lista_variables)
                if category not in categorias:
                    categorias.append(category)
                offerMatch = re_oferta.match(prod_description.lower())
                if offerMatch != None:
                    offer = offerMatch.group(2) + "x" + offerMatch.group(4)
                    insertar(cursor, "Oferta", [prod_id, offer])
            flag = True
        archivo_productos.close() 

        crear_views(cursor,categorias)
        
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
                    # else no pasa nada ¿?¿?
                else:
                    agregar = input("Si desea agregar uno de estos productos al carrito, escriba el ID del producto: ")
                    if agregar in busqueda[1:]:
                        cantidad = int(input("Cuantas unidades desea agregar?: "))
                        agregar_al_carrito(cursor, agregar, cantidad)
            else:
                print("Producto no encontrado")


            '''
            cursor.execute("SELECT * FROM Productos WHERE prod_name='"+ prod_buscado +"'")
            prod_encontrado = cursor.fetchall()
            if len(prod_encontrado) > 0:
                for prod in prod_encontrado:
                    print("Nombre: " + prod[1])
                    print("Descripción: " + prod[2])
                    print("Precio: " + str(prod[5]))
                    #ademas agregar una forma de agregar el producto al carro##########################
            else:
                print("Producto no encontrado")
            '''

        elif opcion == 2:
            top5(cursor)

        elif opcion == 3:
            opcion_categoria = 0
            while opcion_categoria != len(categorias):
                print("Categorias disponibles:")
                contador = 0
                linea_categoria = "{:>2}. {}"
                for categoria in categorias:
                    #print(str(contador+1) + ". " + categoria)
                    print(linea_categoria.format(contador+1,categoria))
                    contador+=1
                #print (str(contador+1)+ ". Volver")
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
                            print("------------------------------")
                            print("Nombre: " + prod[0])
                            print("Descripción: " + prod[1])
                            print("Precio: " + str(prod[2]))
                            print("------------------------------")
                        #ademas agregar una forma de agregar productos al carro##########################

        elif opcion == 4:
            cursor.execute("SELECT * FROM Carrito")
            prod_encontrado = cursor.fetchall()
            if len(prod_encontrado) > 0:
                for prod in prod_encontrado:
                    print("------------------------------")
                    print("Nombre: " + prod[1])
                    print("Descripción: " + prod[2])
                    print("Precio: " + str(prod[5]))
                    print("------------------------------")
            else:
                print("Carrito Vacio")

        elif opcion == 5:
            cursor.execute("SELECT * FROM Carrito")
            prod_encontrado = cursor.fetchall()
            if len(prod_encontrado) > 0:
                for prod in prod_encontrado:
                    print("Nombre: " + prod[1])
                    print("Descripción: " + prod[2])
                    print("Precio: " + str(prod[5]))
                nombre_prod = input("Ingrese el nombre del producto que desea eliminar: ")
                cursor.execute("DELETE FROM Productos WHERE prod_name='" + nombre_prod + "'")
            else:
                print("Carrito Vacio")

        elif opcion == 6:
            cursor.execute("DELETE FROM Carrito")
            print("Carrito vaciado")

        elif opcion == 7:
            #generar boleta
            print("Compra finalizada")

        else:
            print("Opcion invalida, reintente")
            
 
    
    
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()