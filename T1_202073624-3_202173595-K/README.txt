Integrante 1: Eduardo García Orellana
Rol: 202073624-3
Integrante 2: Alexander Inostroza Rubilar
Rol: 202173595-K

Consideraciones del codigo:

1) Para ingresar los codigos de los productos a la tabla correspondiente se utilizó un bigint y no un int debido a que los numeros eran demasiado grandes para ser int
2) Para indentificar las ofertas se utilizó la siguiente expresion regular: r".*pag(a|ue) (\d+) *llev(a|e) (\d+).?\n?$"
3) Para conectarse, se debe agregar la información de conexión en la variable str_de_conexion, como se ve en las lineas 24 y 25.