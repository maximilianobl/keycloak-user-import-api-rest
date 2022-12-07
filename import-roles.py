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

#CLIENT_ID=input("- Ingrese el client_id: ")

username=input("- Ingrese el username: ").replace('"',"'")

from getpass import getpass
password = getpass("- Ingrese el password: ").replace('"',"'")

def get_token():
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



# Asociamos roles al usuario
def create_rol(token: str):

    print('\n************ INSERTANDO ROLES ************')

    with open('roles.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            
            rol_csv = row["nombre"]

            # Roles por reino
            if (row["es_cliente"] == '0'):
                if(rol_csv !=''):
                    url = BASE_URL + "/admin/realms/"+ REALM_URL + "/roles/"+ rol_csv               

                    headers = {
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json",
                                'Accept': 'application/json'
                            }
                    payload={}

                    responseGetRealmRol = requests.get(
                            url,
                            headers=headers,
                            data=payload
                        ) 

                    if (responseGetRealmRol.status_code==404):     

                        #rol_name=json.loads(responseGetRealmRol.text)['name']

                        url = BASE_URL + "/admin/realms/"+ REALM_URL + "/roles"

                        payload = json.dumps({
                                "name": rol_csv,
                                "composite": False,
                                "clientRole": False,
                                "description": row["descripcion"]
                            })
                        
                        responsePostRealmRol = requests.post(
                            url,
                            headers=headers,
                            data=payload
                        ) 

                        if (responsePostRealmRol.status_code==201):
                            print('Response[%s] - REALM ROL: %s: %s ' % (responsePostRealmRol.status_code, rol_csv, '{"OK": "Rol creado con éxito"}'))
                        else:
                            print('Response[%s] - REALM ROL: %s: %s ' % (responsePostRealmRol.status_code, rol_csv, responsePostRealmRol.text))
                    else:
                            print('Response[%s] - REALM ROL: %s: %s ' % (responseGetRealmRol.status_code, rol_csv, '{"ERROR": "El rol ya existe en el Realm"}'))
                else:
                    print('Response[%s] - REALM ROL: %s: %s ' % ('500', 'null', '{"ERROR": "El rol no fue cargado correctamente en el csv"}'))
            
            # Roles por cliente
            elif (row["es_cliente"] == '1'):
                if(rol_csv !='' and row["client_id"] !=''):

                    client_id = get_client_id(token, row["client_id"])

                    #if(client_id != '0'):

                    url_client_rol = BASE_URL + "/admin/realms/"+ REALM_URL + "/clients/"+ client_id + "/roles?search=" + rol_csv

                    headers = {
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json",
                                'Accept': 'application/json'
                            }

                    payload={}

                    responseGetRolClient = requests.get(
                            url=url_client_rol,
                            headers=headers,
                            data=payload
                        ) 
                    
                    if (responseGetRolClient.status_code==200):
                        if (responseGetRolClient.text == '[]'):                        
                            
                            url = BASE_URL + "/admin/realms/"+ REALM_URL + "/clients/"+ client_id +"/roles"

                            payload = json.dumps({
                                    "name": rol_csv,
                                    "composite": False,
                                    "clientRole": False,
                                    "description": row["descripcion"]
                                })

                            responsePostClientRol = requests.post(
                                url,
                                headers=headers,
                                data=payload
                            ) 


                            if (responsePostClientRol.status_code==201):
                                print('Response[%s] - CLIENT ROL: %s: %s ' % (responsePostClientRol.status_code, rol_csv, '{"OK": "Rol creado con éxito"}'))
                            else:
                                print('Response[%s] - CLIENT ROL: %s: %s ' % (responsePostClientRol.status_code, rol_csv, responsePostClientRol.text))
                        else:
                            print('Response[%s] - CLIENT ROL: %s: %s ' % ('500', rol_csv, '{"ERROR": "El rol ya existe en el cliente"}'))
                    else:
                        print('Response[%s] - CLIENT ROL: %s: %s ' % (responseGetRolClient.status_code, rol_csv, responseGetRolClient.text))
                else:
                    print('Response[%s] - CLIENT ROL: %s: %s ' % ('500', rol_csv, '{"ERROR": "El rol o el client_id no fueron cargados correctamente en el csv"}'))

            print('\n')
            line_count += 1



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
        client_id = '0'
    return client_id


if __name__ == '__main__':
    token = get_token()
    if (token != None):
        print('************ ACCESS TOKEN ************\n'+token)
        user = create_rol(token)
    else:
        print('No se pudo obtener el access_token. Verifique los datos ingresados.')