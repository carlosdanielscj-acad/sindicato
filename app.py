from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 's3cr3t'

# Definindo o caminho do banco de dados
DATABASE = 'instance/users.db'

# Conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')  # Configura o modo WAL
    return conn

# Inicializar o banco de dados, caso não exista
def init_db():
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

# Rota de registro de nomes
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    if name:
        try:
            with get_db_connection() as conn:  # Usando o with para garantir que a conexão será fechada
                cursor = conn.cursor()
                
                # Verifica se o nome já existe
                cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    flash('Nome já registrado, tente outro.', 'error')
                    return redirect(url_for('index'))
                
                # Insere o nome no banco de dados com um valor padrão para o campo de senha
                default_password = '1234'  # Um valor fictício para o campo 'password'
                cursor.execute('INSERT INTO users (name, password) VALUES (?, ?)', (name, default_password))
                conn.commit()
                
                flash(f'Nome "{name}" registrado com sucesso!', 'success')
                return redirect(url_for('index'))
        except sqlite3.OperationalError:
            flash('Erro ao acessar o banco de dados. Tente novamente.', 'error')
            return redirect(url_for('index'))
    else:
        flash('Por favor, insira um nome.', 'error')
        return redirect(url_for('index'))

# Rota de login de administrador
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'admin' and password == '1978':
        return redirect(url_for('dashboard'))
    else:
        flash('Credenciais inválidas', 'error')
        return redirect(url_for('index'))

# Rota da dashboard de administração
@app.route('/dashboard')
def dashboard():
    with get_db_connection() as conn:  # Usando o with para garantir que a conexão será fechada
        users = conn.execute('SELECT * FROM users').fetchall()
    return render_template('dashboard.html', users=users)

# Rota para excluir usuário
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
        flash('Usuário excluído com sucesso!', 'success')
    except sqlite3.OperationalError:
        flash('Erro ao excluir o usuário. Tente novamente.', 'error')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
