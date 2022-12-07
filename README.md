# keycloak-user-import-api-rest
Script Python para importar usuarios, grupos y roles desde un csv.
Además, al finalizar la importación, envía un email al usuario con un token temporal para que active su email y modifique su password.

El proyecto cuenta con dos scripts de Python, cada uno con su archivo csv correspondiente. 

Uno es para dar de alta los roles en **Realm Rol** o en los roles del **Client**.

El otro es para automatizar el registro de usuarios, asociar sus grupos y roles aprovechando las API REST de Keycloak.

> Se utilizó para la versión de Keycloak:20.0.1

## Configuraciones en Keycloak
> Si se utiliza el script de `python3 import-roles.py`, obviar estas configuraciones.

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

## Para iniciar la importación
Primero creamos los roles con:  `python3 import-roles.py`, si todo se creó correctamente, utilizar el otro script.

Creamos los usuarios, asociamos sus roles y grupos: `python3 import-users.py`
    
> Es importante que los roles y grupos cargados en el csv y que se desean relacionar a los usuarios existan previamente en Keycloak.
