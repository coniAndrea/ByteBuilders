import os
import click
import requests
from flask import Flask, render_template, request, session, redirect, jsonify
from flaskext.mysql import MySQL
import random
from webpay import WebPay.webpay_plus
#from webpay.webpay_plus import WebpayPlus
#.webpay_plus.transactions
#from webpay.trasaction import TransactionCreateResponse

app = Flask(__name__)
app.secret_key = 'your-secret-key'
#app.run(host = '192.168.147.166', port = 5000)

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
    conexion= mysql.connect()
    print(conexion)
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validar que todos los campos estén completos
        if not (email and first_name and last_name and username and password and confirm_password):
            error = 'Por favor, completa todos los campos.'
            return render_template('register.html', error=error)

        # Validar que el usuario no exista
        conexion = mysql.connect()
        cursor = conexion.cursor()

        sql = "SELECT * FROM users WHERE username = %s "
        datos = (username)
        cursor.execute(sql, datos)
        user = cursor.fetchone()

        if username=="username":
            error = 'El nombre de usuario ya está en uso.'
            return render_template('register.html', error=error)

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            error = 'Las contraseñas no coinciden.'
            return render_template('register.html', error=error)

        # Registro BD
        sql="INSERT INTO `users` (`user_id`, `email`, `first_name`, `last_name`, `username`, `password`, `balance`) VALUES (NULL, %s, %s, %s, %s, %s, 0);"
        datos=(email, first_name, last_name, username, password)

        cursor=conexion.cursor()
        cursor.execute(sql, datos)
        conexion.commit()

        session['username'] = user
        return redirect('/dashboard')

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
    if 'user' in session:
        user = session['user']
        if user:
            return render_template('dashboard.html', user=user)

    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


# Configura la integración de Webpay con los detalles de tu comercio
webpay_plus = WebpayPlus(
    commerce_code='tu_codigo_de_comercio',
    api_key='tu_api_key',
    integration_type='TEST',  # Cambia a 'LIVE' en producción
    return_url='https://tu_url_de_retorno.com'
)


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' in session:
        sender = session['user']
        return render_template('transfer.html', user=sender)

    sender_username = session.get('username')
    if not sender_username:
        return redirect('/login')

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (sender_username,))
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
        receiver_username = request.form['receiver']
        amount = int(request.form['amount'])

        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (receiver_username,))
        receiver_data = cursor.fetchone()

        if not receiver_data:
            error = 'El destinatario no existe.'
            return render_template('transfer.html', user=sender, error=error)

        receiver = {
            'username': receiver_data[4],
            'email': receiver_data[1],
            'first_name': receiver_data[2],
            'last_name': receiver_data[3],
            'balance': receiver_data[6]
        }

        if amount <= 0 or amount > sender['balance']:
            error = 'Monto inválido.'
            return render_template('transfer.html', user=sender, error=error)

        # Crea la transacción utilizando WebpayPlus
        transaction = webpay_plus.TransactionCreate(
            buy_order='orden_de_compra',
            session_id='ID_de_sesion',
            amount=amount,
            return_url=webpay_plus.return_url
        )

        # Redirige al usuario a la URL de Webpay para completar el pago
        return redirect(transaction.url)

    return render_template('transfer.html', user=sender)

@app.route('/reload', methods=['GET', 'POST'])
def reload_balance():
    if 'user' in session:
        user = session['user']
        return render_template('reload.html', user=user)

    username = session.get('username')
    if not username:
        return redirect('/login')

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    user_data = cursor.fetchone()

    if not user_data:
        return redirect('/login')

    user = {
        'username': user_data[4],
        'email': user_data[1],
        'first_name': user_data[2],
        'last_name': user_data[3],
        'balance': user_data[6]
    }

    if request.method == 'POST':
        amount = int(request.form['amount'])
        if amount <= 0:
            error = 'Monto inválido.'
            return render_template('reload.html', user=user, error=error)

        # Crea la transacción utilizando WebpayPlus
        transaction = webpay_plus.TransactionCreate(
            buy_order='orden_de_compra',
            session_id='ID_de_sesion',
            amount=amount,
            return_url=webpay_plus.return_url
        )

        # Redirige al usuario a la URL de Webpay para completar el pago
        return redirect(transaction.url)

    return render_template('reload.html', user=user)

@app.route('/retorno', methods=['GET'])
def retorno():
    if 'user' in session:
        user = session['user']
        return render_template('retorno.html', user=user)

    return redirect('/login')


#Mostrar los datos de la BD como api
@app.route('/api/v1/api_saludo', methods=['GET'])
def api_saludo():
    # response = requests.get("https://musicpro.bemtorres.win/api/v1/test/saludo")
    response = requests.get("https://musicpro.bemtorres.win/api/v1/test/saldo")
    # print(response)
    resp = response.json()
    return str(resp["saldo"])
    # return resp['message']

@app.route('/api/v1/correo', methods=['GET'])
def api_correo():
    response = requests.post("https://musicpro.bemtorres.win/api/v1/musicpro/send_email",
                                data = {
                                    'correo':'di.toro@duocuc.cl',
                                    'asunto':'reprobado',
                                    'contenido':'ha reprobado :( nos vemos en TAV'
                                }
                            )
    # print(response)
    resp = response.json()
    return resp
    # return resp['message']

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
            usuario={'user_id':fila[0], 'email':fila[1], 'first_name':fila[2], 'last_name':fila[3], 'username':fila[4], 'password':fila[5], 'balance':fila[6]}
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
            usuario={'user_id':datos[0], 'email':datos[1], 'first_name':datos[2], 'last_name':datos[3], 'username':datos[4], 'password':datos[5], 'balance':datos[6]}
            return jsonify({'usuarios':usuario,'message':"Usuario Encontrado."})
        else:
            return jsonify({'message':"Usuario no encontrado."})
    except Exception as ex:
        return jsonify({'message':"Error"})

@app.route('/usuario', methods=['POST'])
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

  

@app.route('/usuario/<codigo>', methods=['DELETE'])
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

@app.route('/usuario/<codigo>', methods=['PUT'])
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


