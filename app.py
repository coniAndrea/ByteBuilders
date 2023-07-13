import os
import click
import requests
from flask import Flask, render_template, request, session, redirect, jsonify, Response, Request
from flaskext.mysql import MySQL
import random
import json
import base64
from flask.views import MethodView
import requests
import uuid
from view_client import client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import tkinter as tk

app = Flask(__name__)

# app.register_blueprint(client, url_prefix='/client')
app.register_blueprint(client, url_prefix='/admin')

app.secret_key = 'your-secret-key'

# app.run(host = '0.0.0.0', port = 5000)

# CONEXIÓN MYSQL

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bytebuilders'
mysql.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    conexion = mysql.connect()

    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not (email and first_name and last_name and username and password and confirm_password):
            error = 'Por favor, completa todos los campos.'
            return render_template('register.html', error=error)

        cursor = conexion.cursor()
        sql = "SELECT * FROM users WHERE username = %s"
        datos = (username,)
        cursor.execute(sql, datos)
        user = cursor.fetchone()

        if user:
            error = 'El nombre de usuario ya está en uso.'
            return render_template('register.html', error=error)

        if password != confirm_password:
            error = 'Las contraseñas no coinciden.'
            return render_template('register.html', error=error)

        sql = "INSERT INTO `users` (`user_id`, `email`, `first_name`, `last_name`, `username`, `password`, `balance`) VALUES (NULL, %s, %s, %s, %s, %s, 0)"
        datos = (email, first_name, last_name, username, password)
        cursor.execute(sql, datos)
        conexion.commit()

        session['user'] = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'balance': 0
        }

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        data = (username, password)
        cursor.execute(sql, data)
        user = cursor.fetchone()

        if user:
            session['user'] = {
                'username': user[4],
                'email': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'balance': user[6]
            }
            return redirect('/dashboard')
        else:
            error = 'Credenciales inválidas. Por favor, intenta de nuevo.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')

    if not user:
        return redirect('/login')

    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    sender = session.get('user')

    if not sender:
        return redirect('/login')

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (sender['username'],))
    sender_data = cursor.fetchone()

    if not sender_data:
        return redirect('/login')

    sender = {
        'username': sender_data[4],
        'email': sender_data[1],
        'first_name': sender_data[2],
        'last_name': sender_data[3],
        'balance': sender_data[6]
    }

    if request.method == 'POST':

        monto =  request.form['amount']

        response = requests.post("https://musicpro.bemtorres.win/api/v1/musicpro/send_email",
                                data={
                                    'correo':'ni.munozv@duocuc.cl',
                                    'asunto':'Transferencia exitosa',
                                    'contenido':'Ha transferido el siguiente monto: $' + monto
                                }
                            )
        print(response)
        
        return render_template('transfer.html')
    else:
        return render_template('transfer.html')

  # if 'user' in session:
    #     sender = session['user']
    #     return render_template('transfer.html', user=sender)

    # sender_username = session.get('username')
    # if not sender_username:
    #     return redirect('/login')
    # sender_username = ('carlos_001') 

    # conn = mysql.connect()
    # cursor = conn.cursor()

    # sql = "SELECT * FROM users WHERE username = %s"
    # cursor.execute(sql, (sender_username))
    # sender_data = cursor.fetchone()

    # if not sender_data:
    #     return redirect('/login')

    # sender = {
    #     'username': sender_data[4],
    #     'email': sender_data[1],
    #     'first_name': sender_data[2],
    #     'last_name': sender_data[3],
    #     'balance': sender_data[6]
    # }
    # print(sender)
    # if request.method == 'POST':
    #     receiver_username =
    #     amount = int(request.form['balance'])

    #     sql = "SELECT * FROM users WHERE username = %s"
    #     cursor.execute(sql, (receiver_username,))
    #     receiver_data = cursor.fetchone()

    #     if not receiver_data:
    #         error = 'El destinatario no existe.'
    #         return render_template('transfer.html', user=sender, error=error)

    #     receiver = {
    #         'username': receiver_data[4],
    #         'email': receiver_data[1],
    #         'first_name': receiver_data[2],
    #         'last_name': receiver_data[3],
    #         'balance': receiver_data[6]
    #     }

    #     print(receiver)

    #     if 'amount' <= 0 or amount > sender['balance']:
    #         error = 'Monto inválido.'
    #         return render_template('transfer.html', user=sender, error=error)

    #     sender['balance'] -= amount
    #     receiver['balance'] += amount

    #     sql = "UPDATE users SET balance = %s WHERE username = %s"
    #     cursor.execute(sql, (sender['balance'], sender['username']))
    #     cursor.execute(sql, (receiver['balance'], receiver['username']))
    #     conn.commit()

    #     return redirect('/dashboard')

#INTEGRACION TRANSFERENCIA PROFE
@app.route('/transfer_api', methods=['GET', 'POST'])
def transfer_api():
    if request.method == 'POST':
        receiver_username = request.form['receiver']
        amount = int(request.form['amount'])

        print(request.data)
        response = requests.post("https://musicpro.bemtorres.win/api/v1/tarjeta/transferir",
            data={
                'tarjeta_origen': 'ninoska',
                'tarjeta_destino': receiver_username,
                'comentario': 'PAGO NINOSKA PAY',
                'monto': amount,
                'codigo': 'DEMOMUSICPRO',
                'token': 'NIN-2707e',
            }
        )
        print(response)
        resp = response.json()
        return resp

    return render_template('transfer_api.html')

@app.route('/reload', methods=['GET', 'POST'])
def reload_balance():
    user = session.get('user')

    if not user:
        return redirect('/login')

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (user['username'],))
    user_data = cursor.fetchone()

    if not user_data:
        return redirect('/login')

    user['balance'] = user_data[6]

    if request.method == 'POST':
        amount = int(request.form['amount'])
        if amount <= 0:
            error = 'Monto inválido.'
            return render_template('reload.html', user=user, error=error)

        new_balance = user['balance'] + amount
        sql = "UPDATE users SET balance = %s WHERE username = %s"
        cursor.execute(sql, (new_balance, user['username']))
        conn.commit()

        return redirect('/dashboard')

    return render_template('reload.html', user=user)

#INTEGRACIONES#

@app.route('/api/v1/api_saldo', methods=['GET'])
def api_saludo():
    # response = requests.get("https://musicpro.bemtorres.win/api/v1/test/saludo")
    response = requests.get("https://musicpro.bemtorres.win/api/v1/test/saldo")
    # print(response)
    resp = response.json()
    return str(resp["saldo"])
    # return resp['message']

# INTEGRACIÓN API TRANSFERENCIA
@app.route('/api/v1/transferencia', methods=['POST'])
def api_transferencia():
    # response = requests.get("https://musicpro.bemtorres.win/api/v1/test/saludo")x
    print('funciona funciona funciona funciona ')
    print(request.data)
    return "ok"

@app.route('/api/v1/correo', methods=['GET'])
def api_correo():
    response = requests.post("https://musicpro.bemtorres.win/api/v1/musicpro/send_email",
                                data = {
                                    'correo':'di.toro@duocuc.cl',
                                    'asunto':'reprobado',
                                    'contenido':'ha reprobado :( nos vemos en TAV'
                                }
                            )
    resp = response.json()
    return resp

#INTEGRACION CON PAYPAL
#clientID = 'AX-6V1UsW4fjHw6oDjV2GiXVymeIZ5Z33wrBoKwe1SjvklcN-KMwlqRoeFGv5ulDNvdrTKysKF4sg0Oc'
#clientSecret = 'EHdjszJmfR5xpGWmjaXxtiGa_uZz69ShL3jxNH1n3yzx8bBvBSeT8Boz5IAhxnm0jObcnrAHYHQjJ1Pl'
@app.route('/efectuado', methods=['GET'])
def efectuado():
    return render_template('efectuado.html')

@app.route('/no_efectuado', methods=['GET'])
def no_efectuado():
    return render_template('no_efectuado.html')

def PaypalToken(client_id, client_secret):
    token_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    token_data = {
        "grant_type": "client_credentials"
    }
    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {0}".format(base64.b64encode((client_id + ":" + client_secret).encode()).decode())
    }

    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    if token_response.status_code == 200:
        return token_response.json()['access_token']
    else:
        return None

@app.route('/paypal/token', methods=['POST'])
def paypal_token():
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')

    access_token = PaypalToken(client_id, client_secret)
    return jsonify({'access_token': access_token})

@app.route('/paypal/create/order', methods=['GET'])
def create_order_view():
    client_id = 'AX-6V1UsW4fjHw6oDjV2GiXVymeIZ5Z33wrBoKwe1SjvklcN-KMwlqRoeFGv5ulDNvdrTKysKF4sg0Oc'
    client_secret = 'EHdjszJmfR5xpGWmjaXxtiGa_uZz69ShL3jxNH1n3yzx8bBvBSeT8Boz5IAhxnm0jObcnrAHYHQjJ1Pl'

    token = PaypalToken(client_id, client_secret)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }
    json_data = {
        "intent": "CAPTURE",
        "application_context": {
           # "notify_url": "https://pesapedia.co.ke",
            "return_url": "/efectuado",
            "cancel_url": "/no_efectuado",
            "brand_name": "ByteBank",
            #"landing_page": "BILLING",
            "shipping_preference": "NO_SHIPPING",
            "user_action": "CONTINUE"
        },
        "purchase_units": [
            {
                "reference_id": "REF-12345",  # Cambia "REF-12345" por tu propio identificador único
                "description": "MusicPro",  # Cambia "MusicPro" por tu propia descripción
                "custom_id": "CUST-" + str(uuid.uuid4()),  # Genera un identificador aleatorio único para custom_id
                "soft_descriptor": "Venta de instrumentos musicales",  # Cambia por una descripción adecuada
                "amount": {
                            "currency_code": "CLP",  # Cambia "USD" por "CLP" para la moneda chilena
                            "value": "10000"  # Cambia "10000" por el valor que deseas cobrar
                        },
            }
        ]
    }
    response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=headers, json=json_data)
    order_id = response.json()['id']
    linkForPayment = response.json()['links'][1]['href']
    return linkForPayment

@app.route('/paypal/capture/order', methods=['POST'])
def capture_order_view():
    token = request.form.get('token')
    captureurl = request.form.get('url')

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }
    response = requests.post(captureurl, headers=headers)
    return Response(response.json())


#MOSTRAR LOS DATOS DE LA BD COMO API 
@app.route('/api/v1/usuario', methods=['GET'])
def listar_usuarios_registrados():
    try:
        conexion= mysql.connect()
        cursor=conexion.cursor()
        sql="SELECT `user_id`, `email`, `first_name`, `last_name`, `username`, `password`, `balance` FROM `users`"
        cursor.execute(sql)
        datos=cursor.fetchall()#fetchall convierte la respuesta en algo entendible para python
        usuarios=[]
        for fila in datos:
            usuario={'user_id':fila[0], 'email':fila[1], 'first_name':fila[2], 'last_name':fila[3],
                      'username':fila[4], 'password':fila[5], 'balance':fila[6]}
            usuarios.append(usuario)
        return jsonify({'Usuarios':usuarios, 'message':"Listado de Usuarios Registrados."})
    except Exception as ex:
        return jsonify({'message':"Error al Cargar"})

@app.route('/api/v1/usuario/<codigo>', methods=['GET'])
def leer_usuario(codigo):
    try:
        conexion= mysql.connect()
        cursor=conexion.cursor()
        sql="SELECT `user_id`, `email`, `first_name`, `last_name`, `username`, `password`, `balance` FROM `users` WHERE user_id = '{0}'".format(codigo)
        cursor.execute(sql)
        datos=cursor.fetchone()
        if datos != None:
            usuario={'user_id':datos[0], 'email':datos[1], 'first_name':datos[2], 'last_name':datos[3], 
                     'username':datos[4], 'password':datos[5], 'balance':datos[6]}
            return jsonify({'usuarios':usuario,'message':"Usuario Encontrado."})
        else:
            return jsonify({'message':"Usuario no encontrado."})
    except Exception as ex:
        return jsonify({'message':"Error"})

@app.route('/api/v1/usuario', methods=['POST'])
def registrar_usuario():
    try:
        conexion= mysql.connect()
        cursor=conexion.cursor()
        sql="INSERT INTO users (email, first_name, last_name, username, password, balance) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}');".format(request.json['email'],request.json['first_name'],request.json['last_name'],request.json['username'],request.json['password'],request.json['balance'])
        cursor.execute(sql)
        conexion.commit()
        return jsonify({'message':"Usuario Registrado"})
    except Exception as ex:
        return jsonify({'message':"Error"})

@app.route('/api/v1/usuario/<codigo>', methods=['DELETE'])
def eliminar_usuario(codigo):
    try:
        conexion= mysql.connect()
        cursor=conexion.cursor()
        sql="DELETE FROM users WHERE user_id ='{0}'".format(codigo)
        cursor.execute(sql)
        conexion.commit()
        return jsonify({'message':"Usuario Eliminado"})
    except Exception as ex:
        return jsonify({'message':"Error"})

@app.route('/api/v1/usuario/<codigo>', methods=['PUT'])
def actualizar_usuario(codigo):
    try:
        conexion= mysql.connect()
        cursor=conexion.cursor()
        sql="UPDATE users SET email='{0}', first_name='{1}', last_name='{2}', username='{3}', password='{4}', balance='{5}' WHERE user_id = '{6}'".format(request.json['email'],request.json['first_name'],request.json['last_name'],request.json['username'],request.json['password'],request.json['balance'], codigo)
        cursor.execute(sql)
        conexion.commit()
        return jsonify({'message':"Usuario Actualizado"})
    except Exception as ex:
        return jsonify({'message':"Error"})
    

#IMPORTAR BASE DE DATO
@app.cli.command("import_db")
@click.argument('file_path', default=os.path.join('bd', 'database.sql'))
def import_db(file_path):
  try:
    conexion= mysql.connect()
    cursor = conexion.cursor()

    # Leer el contenido del archivo SQL
    with open(file_path, 'r',  encoding='utf-8') as f:
      sql_script = f.read()

    # Separar las declaraciones SQL individuales
    statements = sql_script.split(';')

    # Ejecutar cada declaración SQL
    for statement in statements:
      if statement.strip():
        cursor.execute(statement)

    conexion.commit()
    conexion.close()

    click.echo('Base de datos importada con éxito!')
  except Exception as ex:
    click.echo('Error al importar la base de datos')
    click.echo(ex)

if __name__ == '__main__':
  app.run(debug=True)
