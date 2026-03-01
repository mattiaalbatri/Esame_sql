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
        print(f"Errore DB: {e}")
        stats = None
    return render_template('index.html', stats=stats)

@app.route('/athletes')
def athletes():
    athletes_list = []
    
    q = request.args.get('q', '').strip()
    medals = request.args.getlist('medal')
    seasons = request.args.getlist('season')
    sexes = request.args.getlist('sex')
    year = request.args.get('year', '').strip()
    sport = request.args.get('sport', '').strip()
    team = request.args.get('team', '').strip()

    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        query = """
            SELECT a.athlete_id as id, a.name, a.sex, p.age, n.region as team,
                   e.sport, g.game_name as games, p.medal
            FROM Participations p
            JOIN Athletes a ON p.athlete_id = a.athlete_id
            JOIN Games g ON p.game_id = g.game_id
            JOIN Events e ON p.event_id = e.event_id
            JOIN Nations n ON p.noc = n.noc
            WHERE 1=1
        """
        params = []

        if q:
            query += " AND (a.name ILIKE %s OR e.sport ILIKE %s OR n.region ILIKE %s)"
            params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
        
        if medals:
            query += " AND p.medal = ANY(%s)"
            params.append(medals)
            
        if seasons:
            query += " AND g.season = ANY(%s)"
            params.append(seasons)
            
        if sexes:
            query += " AND a.sex = ANY(%s)"
            params.append(sexes)
            
        if year.isdigit():
            query += " AND g.year = %s"
            params.append(int(year))
            
        if sport:
            query += " AND e.sport ILIKE %s"
            params.append(f'%{sport}%')
        if team:
            query += " AND n.noc ILIKE %s"
            params.append(f'%{team}%')

        query += " ORDER BY a.name ASC limit 500"

        cur.execute(query, params)
        athletes_list = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Errore DB: {e}")
        athletes_list = []
        
    return render_template('athletes.html', athletes=athletes_list)

@app.route('/nations')
def nations():
    nations_list = []
    q = request.args.get('q', '').strip()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        query = "SELECT noc AS code, region AS name FROM Nations WHERE 1=1"
        params = []
        
        if q:
            query += " AND (region ILIKE %s OR noc ILIKE %s)"
            params.extend([f'%{q}%', f'%{q}%'])
            
        query += " ORDER BY region ASC"
        
        cur.execute(query, params)
        nations_list = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Errore DB: {e}")
        nations_list = []
        
    return render_template('nations.html', nations=nations_list)

@app.route('/games')
def games():
    games_list = []
    q = request.args.get('q', '').strip()
    seasons = request.args.getlist('season')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        query = "SELECT year, season, game_name, city FROM Games WHERE 1=1"
        params = []
        
        if q:
            query += " AND city ILIKE %s"
            params.append(f'%{q}%')
            
        if seasons:
            query += " AND season = ANY(%s)"
            params.append(seasons)
            
        query += " ORDER BY year DESC, season ASC"
        
        cur.execute(query, params)
        games_list = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Errore DB: {e}")
        games_list = []
        
    return render_template('games.html', games=games_list)

@app.route('/add_athlete', methods=['GET', 'POST'])
def add_athlete():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Estrazione dati dal form
            name = request.form.get('name')
            sex = request.form.get('sex')
            age = request.form.get('age') or None
            height = request.form.get('height') or None
            weight = request.form.get('weight') or None
            team = request.form.get('team')
            noc = request.form.get('noc').upper()
            
            games = request.form.get('games')
            year = request.form.get('year')
            season = request.form.get('season')
            city = request.form.get('city')
            
            sport = request.form.get('sport')
            event_name = request.form.get('event')
            medal = request.form.get('medal')

            # 1. Gestione Nazione
            cur.execute("SELECT noc FROM Nations WHERE noc = %s", (noc,))
            if not cur.fetchone():
                cur.execute("INSERT INTO Nations (noc, region) VALUES (%s, %s)", (noc, team))

            # 2. Gestione Gioco
            cur.execute("SELECT game_id FROM Games WHERE game_name = %s", (games,))
            game_result = cur.fetchone()
            if game_result:
                game_id = game_result[0]
            else:
                cur.execute("SELECT COALESCE(MAX(game_id), 0) + 1 FROM Games")
                game_id = cur.fetchone()[0]
                cur.execute("INSERT INTO Games (game_id, game_name, year, season, city) VALUES (%s, %s, %s, %s, %s)",
                            (game_id, games, int(year), season, city))

            # 3. Gestione Evento
            cur.execute("SELECT event_id FROM Events WHERE event_name = %s", (event_name,))
            event_result = cur.fetchone()
            if event_result:
                event_id = event_result[0]
            else:
                cur.execute("SELECT COALESCE(MAX(event_id), 0) + 1 FROM Events")
                event_id = cur.fetchone()[0]
                cur.execute("INSERT INTO Events (event_id, sport, event_name) VALUES (%s, %s, %s)",
                            (event_id, sport, event_name))

            # 4. Inserimento Atleta
            cur.execute("SELECT COALESCE(MAX(athlete_id), 0) + 1 FROM Athletes")
            new_athlete_id = cur.fetchone()[0]
            cur.execute("INSERT INTO Athletes (athlete_id, name, sex) VALUES (%s, %s, %s)", 
                        (new_athlete_id, name, sex))

            # 5. Inserimento Partecipazione
            cur.execute("""
                INSERT INTO Participations (athlete_id, game_id, event_id, noc, age, height, weight, medal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_athlete_id, game_id, event_id, noc, age, height, weight, medal))

            conn.commit()
            cur.close()
            conn.close()
            
            flash('Atleta e partecipazione registrati con successo.', 'success')
            return redirect(url_for('athletes'))
            
        except Exception as e:
            if conn:
                conn.rollback()
            flash(f"Errore durante l'inserimento: {e}", 'danger')
            
    return render_template('add_athlete.html')

@app.route('/edit_athlete/<int:id>')
def edit_athlete(id):
    flash('Funzionalità di modifica in arrivo.', 'success')
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
        if conn:
            conn.rollback()
        flash(f"Errore durante l'eliminazione: {e}", 'danger')
    return redirect(url_for('athletes'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
