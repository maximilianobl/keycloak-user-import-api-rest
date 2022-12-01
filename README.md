# keycloak-user-import-api-rest
Script python para importar usuarios, grupos y roles desde un csv.
Además, al finalizar envía un email al usuario para que active su email y modifique su password.

Contiene un script de Python y un archivo csv para automatizar el registro de usuarios, asociar sus grupos y roles en Keycloak aprovechando las API REST de Keycloak.
Se utilizó para la versión de Keycloak:20.0.1

# Configuraciones en Keycloak
En el menú de Groups, agregamos los grupos que son los que vamos a relacionar a los usuarios y se encuentran en el csv. 
- devops
- interno
- test

En el menú de Realm roles, agregamos los roles que son los que vamos a relacionar a los usuarios y se encuentran en el csv. 
- admin
- pepito
- user_esp

En la sección Realm Settings, ingresar a la pestaña “Themes” y en la opción Email theme: rus-theme presionar guardar. 
Dentro de esta misma sección pero en la pestaña “Email” configuramos el template y los datos para el smtp. En este caso para el SMTP estamos usando mailhog para facilitar las pruebas en modo desarrollo.

Configurar el SMTP de la siguiente manera:

HOST: mailhog
PORT: 1025

Es posible acceder a la interfaz en la siguiente url: http://localhost:8025/

# Para iniciar la importación
    python3 import-users.py
    
Es importante que los roles y grupos cargados en el csv y que se desean relacionar a los usuarios existan previamente en Keycloak.


