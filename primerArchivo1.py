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


# lista tipos: True si es tipo int, False si no.
productos_tipos = [True, False, False, False, False, True]
carrito_tipos = [True, False, False, True]
boleta_tipos = [True, False, True, True]
oferta_tipos = [True, False]

# str de conexion
#str_de_conexion = "DRIVER={SQL Server};Server=localhost\SQLEXPRESS01;Database=Tarea1;Trusted_Connection=True;" # Alex
str_de_conexion = "DRIVER={SQL Server};SERVER=LAPTOP-LC6S56LJ;DATABASE=MultiUSM;Trusted_Connection=yes;" # Edu


def reset():
    return False

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

def main():
    connection = pyodbc.connect(str_de_conexion)
    cursor = connection.cursor()   

    if not existe_tabla(cursor, "Productos"):
        cursor.execute("CREATE TABLE Productos (prod_id bigint, prod_name VARCHAR(150), prod_description VARCHAR(150), prod_brand VARCHAR(150), category VARCHAR(150), prod_unit_price int)")
        cursor.execute("CREATE TABLE Carrito (prod_id bigint, prod_name VARCHAR(150), prod_brand VARCHAR(150), quantity int)")
        cursor.execute("CREATE TABLE Boleta (prod_id bigint, offer VARCHAR(150), total_value int, final_value int)")
        cursor.execute("CREATE TABLE Oferta (prod_id bigint, offer VARCHAR(150))")

        archivo_productos = open("ProductosVF2.csv","r",encoding="UTF-8")
        flag = False
        re_oferta = re.compile(r".*pag(a|ue) (\d+) *(und)? *llev(a|e) (\d+).\n?")
        categorias = list()
        for linea in archivo_productos:
            if flag:
                lista_variables = linea.replace("'","").strip().split(";")
                prod_id, prod_name, prod_description, prod_brand, category, prod_unit_price = lista_variables
                insertar(cursor, "Productos", lista_variables)
                offerMatch = re_oferta.match(prod_description.lower())
                if category not in categorias:
                    categorias.append(category)
                if offerMatch != None:
                    #print(prod_description)
                    #print("group 2 = ", offerMatch.group(2), " ; group 5 = ", offerMatch.group(5))
                    offer = offerMatch.group(2) + "x" + offerMatch.group(5)
                    #print("offer = ", offer, end = "\n\n")                
            flag = True

        crear_views(cursor,categorias)
            
        opcion = 1
        while opcion != 6:
            print("#################### MENÚ ####################")
            print("1. Buscar producto")
            print("2. Ver Categorias")
            print("3. Mostrar mi carrito")
            print("4. Eliminar un elemento de mi carrito")
            print("5. Limpiar mi carrito")
            print("6. Finalizar compras")
            opcion = int(input("Ingrese un numero:"))

            if opcion == 1:
                prod_buscado = input("Ingrese el nombre del producto: ")
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

            if opcion == 2:
                opcion_categoria = 0
                while opcion_categoria != len(categorias):
                    contador = 0
                    for categoria in categorias:
                        print(str(contador+1) + ". " + categoria)
                        contador+=1
                    print (str(contador+1)+ ". Volver")
                    opcion_categoria = (int(input("Ingrese un numero: "))) - 1

                    if opcion_categoria < 0 or opcion_categoria > len(categorias):
                        print("Opcion invalida, reintente")

                    if opcion_categoria >= 0 and opcion_categoria < len(categorias):
                        cursor.execute("SELECT * FROM " + categorias[opcion_categoria].replace(" ","_").replace(",","_"))
                        prods = cursor.fetchall()
                        for prod in prods:
                            print("------------------------------")
                            print("Nombre: " + prod[0])
                            print("Descripción: " + prod[1])
                            print("Precio: " + str(prod[2]))
                            print("------------------------------")
                        #ademas agregar una forma de agregar productos al carro##########################

            if opcion == 3:
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

            if opcion == 4:
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

            if opcion == 5:
                cursor.execute("DELETE FROM Carrito")
                print("Carrito vaciado")

            if opcion == 6:
                print("Compra finalizada")

            else:
                print("Opcion invalida, reintente")
                
                


    if reset():
        pass
        # eliminar tablas
    
    
    
    connection.commit()
    archivo_productos.close() 
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()