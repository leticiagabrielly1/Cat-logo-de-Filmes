"""Catálogo de Filmes — UC32. CRUD com Flask, Jinja2 e SQLite."""
import math
import os
import secrets
import sqlite3
from pathlib import Path
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
    DATABASE=os.environ.get('DATABASE_PATH', str(Path(__file__).parent / 'filmes.db')),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


def get_db():
    """Abre uma conexão por requisição; Row permite acessar colunas pelo nome."""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'], timeout=20)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """CREATE TABLE IF NOT EXISTS cria a tabela sem apagar os dados existentes."""
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS filmes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL CHECK(length(trim(titulo)) BETWEEN 1 AND 150),
        genero TEXT NOT NULL CHECK(length(trim(genero)) BETWEEN 1 AND 60),
        ano INTEGER NOT NULL CHECK(ano BETWEEN 1888 AND 2100),
        nota REAL NOT NULL CHECK(nota BETWEEN 1 AND 10)
    )''')
    db.commit()


# Executa também quando o Gunicorn importa app:app no Render.
with app.app_context():
    init_db()


@app.context_processor
def template_helpers():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return {'csrf_token': session['csrf_token']}


@app.before_request
def protect_forms():
    if request.method == 'POST':
        expected = session.get('csrf_token', '')
        received = request.form.get('csrf_token', '')
        if not expected or not secrets.compare_digest(expected, received):
            abort(400, description='Formulário expirado. Volte à página inicial e tente novamente.')


def find_movie(movie_id):
    movie = get_db().execute('SELECT * FROM filmes WHERE id = ?', (movie_id,)).fetchone()
    if movie is None:
        abort(404)
    return movie


def validate_form():
    data = {field: request.form.get(field, '').strip() for field in ('titulo', 'genero', 'ano', 'nota')}
    errors = []
    if not 1 <= len(data['titulo']) <= 150:
        errors.append('Informe um título de até 150 caracteres.')
    if not 1 <= len(data['genero']) <= 60:
        errors.append('Informe um gênero de até 60 caracteres.')
    try:
        data['ano'] = int(data['ano'])
        if not 1888 <= data['ano'] <= 2100:
            raise ValueError
    except ValueError:
        errors.append('Informe um ano inteiro entre 1888 e 2100.')
    try:
        data['nota'] = float(data['nota'].replace(',', '.'))
        if not math.isfinite(data['nota']) or not 1 <= data['nota'] <= 10:
            raise ValueError
    except ValueError:
        errors.append('Informe uma nota de 1 a 10.')
    return data, errors


@app.route('/')
def index():
    # READ: consulta os filmes, do mais recente para o mais antigo no cadastro.
    filmes = get_db().execute('SELECT * FROM filmes ORDER BY id DESC').fetchall()
    media = sum(f['nota'] for f in filmes) / len(filmes) if filmes else None
    return render_template('index.html', filmes=filmes, media=media)


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    filme, errors = {}, []
    if request.method == 'POST':
        filme, errors = validate_form()
        if not errors:
            db = get_db()
            # CREATE: placeholders (?) evitam concatenar entradas do usuário no SQL.
            db.execute('INSERT INTO filmes (titulo, genero, ano, nota) VALUES (?, ?, ?, ?)',
                       (filme['titulo'], filme['genero'], filme['ano'], filme['nota']))
            db.commit()
            flash('Filme cadastrado com sucesso!')
            return redirect(url_for('index'))
    return render_template('form.html', filme=filme, errors=errors, editar=False), 400 if errors else 200


@app.route('/editar/<int:movie_id>', methods=['GET', 'POST'])
def editar(movie_id):
    filme, errors = dict(find_movie(movie_id)), []
    if request.method == 'POST':
        filme, errors = validate_form()
        if not errors:
            db = get_db()
            # UPDATE: WHERE limita a alteração ao filme escolhido.
            db.execute('UPDATE filmes SET titulo=?, genero=?, ano=?, nota=? WHERE id=?',
                       (filme['titulo'], filme['genero'], filme['ano'], filme['nota'], movie_id))
            db.commit()
            flash('Filme atualizado com sucesso!')
            return redirect(url_for('index'))
    return render_template('form.html', filme=filme, errors=errors, editar=True), 400 if errors else 200


@app.route('/excluir/<int:movie_id>', methods=['GET', 'POST'])
def excluir(movie_id):
    filme = find_movie(movie_id)
    if request.method == 'POST':
        db = get_db()
        # DELETE: a exclusão só acontece após confirmar o formulário POST.
        db.execute('DELETE FROM filmes WHERE id=?', (movie_id,))
        db.commit()
        flash('Filme excluído com sucesso!')
        return redirect(url_for('index'))
    return render_template('excluir.html', filme=filme)


@app.errorhandler(404)
def not_found(error):
    return render_template('erro.html', mensagem='Este filme ou página não foi encontrado.'), 404


@app.errorhandler(400)
def bad_request(error):
    return render_template('erro.html', mensagem=error.description), 400


if __name__ == '__main__':
    app.run(debug=False)
