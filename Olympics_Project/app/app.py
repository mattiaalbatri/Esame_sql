from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg
from psycopg.rows import dict_row
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'olympia-manager-secret-key-2026')

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'olympics_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')

def get_db_connection():
    conn = psycopg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

@app.route('/')
def index():
    stats = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM Athletes) AS athletes,
                (SELECT COUNT(*) FROM Nations) AS nations,
                (SELECT COUNT(*) FROM Games) AS games,
                (SELECT COUNT(*) FROM Participations WHERE medal != 'NA') AS medals
        """)
        stats = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Errore: {e}")
        stats = None
    return render_template('index.html', stats=stats)

@app.route('/athletes')
def athletes():
    athletes_list = []
    query = request.args.get('q', '').strip()
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        base_query = """
            SELECT a.athlete_id as id, a.name, a.sex, p.age, n.region as team,
                   e.sport, g.game_name as games, p.medal
            FROM Participations p
            JOIN Athletes a ON p.athlete_id = a.athlete_id
            JOIN Games g ON p.game_id = g.game_id
            JOIN Events e ON p.event_id = e.event_id
            JOIN Nations n ON p.noc = n.noc
        """
        
        if query:
            search_query = base_query + """
                WHERE a.name ILIKE %s OR e.sport ILIKE %s OR n.region ILIKE %s
                ORDER BY a.name
                LIMIT 200
            """
            cur.execute(search_query, (f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            cur.execute(base_query + " ORDER BY a.athlete_id DESC LIMIT 200")
            
        athletes_list = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Errore: {e}")
        athletes_list = []
    return render_template('athletes.html', athletes=athletes_list)

@app.route('/add_athlete', methods=['GET', 'POST'])
def add_athlete():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT COALESCE(MAX(athlete_id), 0) + 1 FROM Athletes")
            new_athlete_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO Athletes (athlete_id, name, sex)
                VALUES (%s, %s, %s)
            """, (
                new_athlete_id,
                request.form.get('name'),
                request.form.get('sex')
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            flash('Atleta aggiunto con successo!', 'success')
            return redirect(url_for('athletes'))
        except Exception as e:
            flash(f"Errore durante l'inserimento: {e}", 'error')
    return render_template('add_athlete.html')

@app.route('/edit_athlete/<int:id>')
def edit_athlete(id):
    flash('Funzionalità di modifica in arrivo!', 'success')
    return redirect(url_for('athletes'))

@app.route('/delete_athlete/<int:id>', methods=['POST'])
def delete_athlete(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM Participations WHERE athlete_id = %s", (id,))
        cur.execute("DELETE FROM Athletes WHERE athlete_id = %s", (id,))
        
        conn.commit()
        cur.close()
        conn.close()
        flash('Record eliminato con successo.', 'success')
    except Exception as e:
        flash(f"Errore durante l'eliminazione: {e}", 'error')
    return redirect(url_for('athletes'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')