import csv
import requests
import json
import re

###############################################################################################
# Script para agregar un usuario, sus roles y grupo a Keycloak a través de un archivo CSV
#
###############################################################################################
BASE_URL = "http://localhost:8080"
REALM_URL = input("- Ingrese el nombre del reino: ")
REDIRECT_URL="http://localhost:8080"
# REDIRECT_URI_ENCODED=$(printf %s $REDIRECT_URL | jq -sRr @uri)
CLIENT_ID=input("- Ingrese el client_id: ")

username=input("- Ingrese el username: ").replace('"',"'")

from getpass import getpass
password = getpass("- Ingrese el password: ").replace('"',"'")

def get_token():

    # Actualice la credencial de admin para su instancia de keycloak
    #username='admin'
    #password='admin'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    url = BASE_URL + "/realms/"+ REALM_URL +"/protocol/openid-connect/token"
    data = {
       'client_id': 'admin-cli',       
       'username': username,
       'password': password,
       'grant_type': 'password'
    }

    response = requests.post(
        url,        
        data,
        headers
    ).json()
    return response.get('access_token')




def create_user(token: str):
    
    print('\n************ INSERTANDO USUARIOS ************')

    url = BASE_URL + "/admin/realms/"+ REALM_URL +"/users"

    with open('users_python_rol.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                line_count += 1

            usr_data = {
                "username": row["username"],
                "enabled": 'true',                
                "firstName": row["firstname"],
                "lastName": row["lastname"],
                "email": row["email"],
                "emailVerified": 'false',
                "requiredActions":["VERIFY_EMAIL","UPDATE_PASSWORD"],
                "attributes": {
                    "phone": [row["atr_phone"]],
                    "username_sis": [row["atr_user_sis"]]
                },
                "credentials":[
                    {
                        "type": "password",
                        "value":"password",
                        "temporary":'true'
                    }
                ]
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                'Accept': 'application/json'
            }

            is_mail = validarEmail(row["email"])

            if (is_mail == True):
                response = requests.post(
                    url,
                    data=json.dumps(usr_data),
                    headers=headers
                ) 

                if (response.status_code==201):
                    print('Response[%s] - %s: %s ' % (response.status_code, row["username"], '{"OK": "Usuario añadido con éxito"}'))
                else:
                    print('Response[%s] - %s: %s ' % (response.status_code, row["username"], response.text))

                # Ahora le asignamos el rol al usuario
                if (response.status_code in (201, 409)):
                    if (row['rol'] != ''):
                        user_rol(token, row["username"], row["rol"], CLIENT_ID)
                    if (row['grupo'] != ''):
                        user_group(token, row, row["username"])
                    if (row['email'] != ''):
                        user_email_upd_psw(token, row["username"], row['email'])                
            else:
                print('Response[%s] - EMAIL: %s %s' % ('500', row["email"], '{"WARN": "El formato del email no es correcto, no se procesó el registro"}'))
            
            print('\n')
            line_count += 1
    #return response


# Retonamos el id del usuario desde Keycloak
def get_usr_id(token: str, username):
    
    url = BASE_URL + "/admin/realms/"+ REALM_URL +"/users?username="+ username

    headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                'Accept': 'application/json'
            }
            
    payload={}

    responseUsr = requests.get(
                url,
                headers=headers,
                data=payload
            ) 
    if (responseUsr.text != '[]'):
        usr_id=json.loads(responseUsr.text)[0]['id']
    else:
        usr_id = 'not_exists'
    return usr_id



# Retonamos el id del cliente desde Keycloak
def get_client_id(token: str, clientId):
  
    url = BASE_URL + "/admin/realms/master/clients?clientId=" + clientId

    headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                'Accept': 'application/json'
            }
            
    payload={}

    responseRolClient = requests.get(
            url,
            headers=headers,
            data=payload
        ) 

    if (responseRolClient.text != '[]'):
        client_id=json.loads(responseRolClient.text)[0]['id']
    else:
        client_id = 'not_exists'
    return client_id




# Verificamos formato del email
def validarEmail(email):
   pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,email):
      return True
   return False





# Asociamos roles al usuario
def user_rol(token: str, username, rol, clientId):

    user_id = get_usr_id(token, username)

    # Busco el rol en Realm roles
    url = BASE_URL + "/admin/realms/"+ REALM_URL + "/roles/"+ rol

    headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                'Accept': 'application/json'
            }
    payload={}

    responseRol = requests.get(
            url,
            headers=headers,
            data=payload
        ) 
    
    if (responseRol.status_code==200):     
        rol_id=json.loads(responseRol.text)['id']
        rol_name=json.loads(responseRol.text)['name']

        # Mapeamos el Rol en el Usuario
        url = BASE_URL + "/admin/realms/"+ REALM_URL + "/users/"+ user_id + "/role-mappings/realm"

        responseUsrRol = requests.post(
            url,
            headers=headers,
            data='['+ responseRol.text + ']'
        ) 

        if (responseUsrRol.status_code==204):
            print('Response[%s] - ROL REALM: %s: %s ' % (responseUsrRol.status_code, rol_name, '{"OK": "Rol asociado con éxito"}'))
        else:
            print('Response[%s] - ROL REALM: %s: %s ' % (responseUsrRol.status_code, rol, responseUsrRol.text))
    else:
            print('Response[%s] - ROL REALM: %s: %s ' % (responseRol.status_code, rol, responseRol.text))
    
    
    # Busco el rol en el cliente
    client_id = get_client_id(token, clientId)

    url_client_rol = BASE_URL + "/admin/realms/master/clients/"+ client_id + "/roles?search=" + rol

    responseRolClient = requests.get(
            url=url_client_rol,
            headers=headers,
            data=payload
        ) 
    
    if (responseRolClient.status_code==200):
        if (responseRolClient.text != '[]'):
            # rol_id=json.loads(responseRolClient.text)['id']
            rol_client_name=json.loads(responseRolClient.text)[0]['name']

            # Mapeamos el Rol en el Usuario
            url = BASE_URL + "/admin/realms/"+ REALM_URL + "/users/"+ user_id + "/role-mappings/clients/" + client_id

            responseUsrRol = requests.post(
                url,
                headers=headers,
                data=responseRolClient.text
            ) 

            if (responseUsrRol.status_code==204):
                print('Response[%s] - ROL CLIENT: %s: %s ' % (responseUsrRol.status_code, rol_client_name, '{"OK": "Rol asociado con éxito"}'))
            else:
                print('Response[%s] - ROL CLIENT: %s: %s ' % (responseUsrRol.status_code, rol, responseUsrRol.text))
        else: 
            print('Response[%s] - ROL CLIENT: %s: %s ' % ('500', rol, '{"error":"Could not find role"}'))
    else:
            print('Response[%s] - ROL CLIENT: %s: %s ' % (responseRolClient.status_code, rol, responseRolClient.text))
            





# Asociamos el grupo al usuario
def user_group(token: str, csv_data, username):

    # Obtenemos id del grupo desde Keycloak
    url = BASE_URL + "/admin/realms/"+ REALM_URL +"/groups?search="+ csv_data['grupo']

    headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                'Accept': 'application/json'
            }
            
    payload={}

    responseGroup = requests.get(
                url,
                headers=headers,
                data=payload
            ) 

    if (responseGroup.status_code==200 and responseGroup.text != '[]'):     
            group_id=json.loads(responseGroup.text)[0]['id']
            group_name=json.loads(responseGroup.text)[0]['name']

            # Obtenemos el id de usuario
            user_id = get_usr_id(token, username)
            url = BASE_URL + "/admin/realms/"+ REALM_URL + "/users/"+ user_id + "/groups/"+ group_id

            payload={}

            responseUsrGroup = requests.put(
                url,
                headers=headers,
                data=payload
            ) 

            if (responseUsrGroup.status_code==204):
                print('Response[%s] - GRUPO: %s: %s ' % (responseUsrGroup.status_code, group_name, '{"OK": "Grupo asociado con éxito"}'))
            else:
                print('Response[%s] - GRUPO: %s: %s ' % (responseUsrGroup.status_code, csv_data['grupo'], responseUsrGroup.text))
    else:
                print('Response[%s] - GRUPO: %s: %s ' % (responseGroup.status_code, csv_data['grupo'], {"error":"Could not find group"}
))


# Enviar email para resetear el password
def user_email_upd_psw(token: str, username, email):
    
    # El ftl que se debe modificar es: executeActions.ftl

     # Obtenemos el id de usuario
    user_id = get_usr_id(token, username)
    url = BASE_URL + "/admin/realms/"+ REALM_URL +"/users/"+ user_id +"/execute-actions-email?client_id="+ CLIENT_ID +"&redirect_uri="+ REDIRECT_URL

    headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                'Accept': 'application/json'
            }
   
    payload = json.dumps([
                "UPDATE_PASSWORD","VERIFY_EMAIL" 
            ])

    responseEmailUpdatePassword = requests.put(
                url,
                headers=headers,
                data=payload
        ) 
    
    if (responseEmailUpdatePassword.status_code==204):
        print('Response[%s] - EMAIL: %s: %s ' % (responseEmailUpdatePassword.status_code, email, '{"OK": "Email enviado con éxito"}'))
    else:
        print('Response[%s] - EMAIL: %s: %s ' % (responseEmailUpdatePassword.status_code, email, responseEmailUpdatePassword.text))


# Enviar email para verificar el correo
# url = "http://localhost:8080/admin/realms/master/users/{{userId}}/send-verify-email"

# payload={}
# headers = {
#   'Authorization': 'Bearer {token}'
# }

# response = requests.request("PUT", url, headers=headers, data=payload)




if __name__ == '__main__':
    token = get_token()
    if (token != None):
        print('************ ACCESS TOKEN ************\n'+token)
        user = create_user(token)
    else:
        print('No se pudo obtener el access_token. Verifique el username o el password.')