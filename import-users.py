import csv
import requests
import json

###############################################################################################
# Script para agregar un usuario, sus roles y grupo a Keycloak a través de un archivo CSV
#
###############################################################################################
BASE_URL = "http://localhost:8080"
REALM_URL = "master"


def get_token():

    # Actualice la credencial de admin para su instancia de keycloak
    username='admin'
    password='admin'
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
    url = BASE_URL + "/admin/realms/"+ REALM_URL +"/users"

    print('\n************ INSERTANDO USUARIOS ************')

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
                "emailVerified": 'true',
                "firstName": row["firstname"],
                "lastName": row["lastname"],
                "email": row["email"],
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
                    user_rol(token, row)
                    if (row['grupo'] != ''):
                        user_group(token, row, row["username"])

            line_count += 1
    return response

def get_usr_id(token: str, username):
    # Obtenemos id, username del usuario desde Keycloak
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


    # Obtener datos del rol
    # if (responseUsr.status_code==200):
    #     usr_id=json.loads(responseUsr.text)[0]['id']





def user_rol(token: str, csv_data):

    # Obtenemos id, username del usuario desde Keycloak
    url = BASE_URL + "/admin/realms/"+ REALM_URL +"/users?username="+ csv_data['username']

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


    # Obtener datos del rol
    if (responseUsr.status_code==200):

        usr_id=json.loads(responseUsr.text)[0]['id']
        user_name=json.loads(responseUsr.text)[0]['username']

        url = BASE_URL + "/admin/realms/"+ REALM_URL + "/roles/"+ csv_data['rol']

        responseRol = requests.get(
                url,
                headers=headers,
                data=payload
            ) 

        if (responseRol.status_code==200):     
            rol_id=json.loads(responseRol.text)['id']
            rol_name=json.loads(responseRol.text)['name']

            # Mapeamos el Rol en el Usuario
            url = BASE_URL + "/admin/realms/"+ REALM_URL + "/users/"+ usr_id + "/role-mappings/realm"

            #responseUsrRol = requests.request("POST", getRolUsrUrl, headers=headers_json, data='['+responseRol.text+']')

            responseUsrRol = requests.post(
                url,
                headers=headers,
                data='['+ responseRol.text + ']'
            ) 

            if (responseUsrRol.status_code==204):
                print('Response[%s] - USR: %s ,ROL: %s: %s ' % (responseUsrRol.status_code, user_name, rol_name, '{"OK": "Rol asociado con éxito"}'))
            else:
                print('Response[%s] - USR: %s ,ROL: %s: %s ' % (responseUsrRol.status_code, user_name, csv_data['rol'], responseUsrRol.text))
        else:
                print('Response[%s] - ROL: %s: %s ' % (responseRol.status_code, csv_data['rol'], responseRol.text))


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
                print('Response[%s] - USR: %s ,GRUPO: %s: %s ' % (responseUsrGroup.status_code, username, group_name, '{"OK": "Grupo asociado con éxito"}'))
            else:
                print('Response[%s] - USR: %s ,GRUPO: %s: %s ' % (responseUsrGroup.status_code, username, csv_data['grupo'], responseUsrGroup.text))
    else:
                print('Response[%s] - GRUPO: %s: %s ' % (responseGroup.status_code, csv_data['grupo'], {"error":"Could not find group"}
))



if __name__ == '__main__':
    token = get_token()
    print('************ ACCESS TOKEN ************\n'+token)
    user = create_user(token)