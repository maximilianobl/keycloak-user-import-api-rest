# keycloak-user-import-api-rest
Script python para importar usuarios, grupos y roles desde un csv.
Además, al finalizar envía un email al usuario para que active su email y modifique su password.

Contiene un script de Python y un archivo csv para automatizar el registro de usuarios, asociar sus grupos y roles en Keycloak aprovechando las API REST de Keycloak.
Se utilizó para la versión de Keycloak:20.0.1

# Para iniciar la importación
    python3 import-users.py
    
Es importante que los roles y grupos cargados en el csv y que se desean relacionar a los usuarios existan previamente en Keycloak.

