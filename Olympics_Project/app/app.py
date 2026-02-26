from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'olympia-manager-secret-key-2026')

# Configurazione Database (usando variabili d'ambiente per Docker)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'olympics_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn


# ──────────────────────────────────────────────
# HOME / DASHBOARD
# ──────────────────────────────────────────────
@app.route('/')
def index():
    stats = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                COUNT(DISTINCT name) AS athletes,
                COUNT(DISTINCT noc) AS nations,
                COUNT(DISTINCT games) AS games,
                COUNT(*) FILTER (WHERE medal != 'NA') AS medals
            FROM athlete_events
        """)
        stats = cur.fetchone()
        cur.close()
        conn.close()
    except Exception:
        stats = None
    return render_template('index.html', stats=stats)


# ──────────────────────────────────────────────
# LISTA ATLETI / RICERCA
# ──────────────────────────────────────────────
@app.route('/athletes')
def athletes():
    athletes_list = []
    query = request.args.get('q', '').strip()
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if query:
            cur.execute("""
                SELECT id, name, sex, age, team, sport, games, medal
                FROM athlete_events
                WHERE name ILIKE %s OR sport ILIKE %s OR team ILIKE %s OR games ILIKE %s
                ORDER BY name
                LIMIT 200
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            cur.execute("""
                SELECT id, name, sex, age, team, sport, games, medal
                FROM athlete_events
                ORDER BY id DESC
                LIMIT 200
            """)
        athletes_list = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        athletes_list = []
    return render_template('athletes.html', athletes=athletes_list)


# ──────────────────────────────────────────────
# AGGIUNGI ATLETA
# ──────────────────────────────────────────────
@app.route('/add_athlete', methods=['GET', 'POST'])
def add_athlete():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO athlete_events
                    (name, sex, age, height, weight, team, noc, games, year, season, city, sport, event, medal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form.get('name'),
                request.form.get('sex'),
                request.form.get('age') or None,
                request.form.get('height') or None,
                request.form.get('weight') or None,
                request.form.get('team'),
                request.form.get('noc', '').upper(),
                request.form.get('games'),
                request.form.get('year'),
                request.form.get('season'),
                request.form.get('city'),
                request.form.get('sport'),
                request.form.get('event'),
                request.form.get('medal', 'NA'),
            ))
            conn.commit()
            cur.close()
            conn.close()
            flash('Atleta aggiunto con successo!', 'success')
            return redirect(url_for('athletes'))
        except Exception as e:
            flash(f'Errore durante l\'inserimento: {e}', 'error')
    return render_template('add_athlete.html')


# ──────────────────────────────────────────────
# MODIFICA ATLETA (placeholder)
# ──────────────────────────────────────────────
@app.route('/edit_athlete/<int:id>')
def edit_athlete(id):
    # TODO: implementare pagina di modifica
    flash('Funzionalità di modifica in arrivo!', 'success')
    return redirect(url_for('athletes'))


# ──────────────────────────────────────────────
# ELIMINA ATLETA
# ──────────────────────────────────────────────
@app.route('/delete_athlete/<int:id>', methods=['POST'])
def delete_athlete(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM athlete_events WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Record eliminato con successo.', 'success')
    except Exception as e:
        flash(f'Errore durante l\'eliminazione: {e}', 'error')
    return redirect(url_for('athletes'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')