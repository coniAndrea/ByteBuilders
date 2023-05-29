from flask import Flask, render_template, request, session, redirect
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Base de datos simulada de usuarios
users = {
    'user1': {
        'email': 'user1@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'password1',
        'balance': 1000
    },
    'user2': {
        'email': 'user2@example.com',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'password': 'password2',
        'balance': 500
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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
        if username in users:
            error = 'El nombre de usuario ya está en uso.'
            return render_template('register.html', error=error)

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            error = 'Las contraseñas no coinciden.'
            return render_template('register.html', error=error)

        # Registrar el usuario
        users[username] = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'balance': 0
        }

        session['username'] = username
        return redirect('/dashboard')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validar las credenciales de inicio de sesión
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect('/dashboard')
        else:
            error = 'Credenciales inválidas. Por favor, intenta de nuevo.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        user = users.get(username)
        if user:
            return render_template('dashboard.html', user=user)
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/transfer', methods=['POST'])
def transfer():
    username = session.get('username')
    if not username:
        return redirect('/login')

    sender = users.get(username)
    if not sender:
        return redirect('/login')

    receiver_username = request.form['receiver']
    amount = int(request.form['amount'])

    receiver = users.get(receiver_username)
    if not receiver:
        error = 'El destinatario no existe.'
        return render_template('dashboard.html', user=sender, error=error)

    if amount <= 0 or amount > sender['balance']:
        error = 'Monto inválido.'
        return render_template('dashboard.html', user=sender, error=error)

    sender['balance'] -= amount
    receiver['balance'] += amount

    return redirect('/dashboard')

@app.route('/reload', methods=['POST'])
def reload_balance():
    username = session.get('username')
    if not username:
        return redirect('/login')

    user = users.get(username)
    if not user:
        return redirect('/login')

    amount = int(request.form['amount'])
    if amount <= 0:
        error = 'Monto inválido.'
        return render_template('dashboard.html', user=user, error=error)

    user['balance'] += amount

    return redirect('/dashboard')

@app.route('/pay', methods=['POST'])
def make_payment():
    username = session.get('username')
    if not username:
        return redirect('/login')

    user = users.get(username)
    if not user:
        return redirect('/login')

    amount = int(request.form['amount'])
    if amount <= 0 or amount > user['balance']:
        error = 'Monto inválido.'
        return render_template('dashboard.html', user=user, error=error)

    user['balance'] -= amount

    return redirect('/dashboard')

def generate_card_number():
    # Generar un número de tarjeta de 16 dígitos
    card_number = ''.join(random.choice('0123456789') for _ in range(16))
    return card_number

if __name__ == '__main__':
    app.run(debug=True)
