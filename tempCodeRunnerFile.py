nombre_prod = input("Ingrese el nombre del producto que desea eliminar: ")
                cursor.execute("DELETE FROM Productos WHERE prod_name='" + nombre_prod + "'")