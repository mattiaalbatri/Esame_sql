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
    return psycopg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

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
    except Exception:
        stats = None
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
    return render_template('index.html', stats=stats)

@app.route('/athletes')
def athletes():
    athletes_list = []
    
    q = request.args.get('q', '').strip()
    team = request.args.get('team', '').strip()
    game_filter = request.args.get('games', '').strip()
    medals = request.args.getlist('medal')
    seasons = request.args.getlist('season')
    sexes = request.args.getlist('sex')
    year = request.args.get('year', '').strip()
    sport = request.args.get('sport', '').strip()
    
    page = request.args.get('page', 1, type=int)
    limit = 500
    offset = (page - 1) * limit

    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        query = """
            SELECT a.athlete_id as id, a.name, a.sex, 
                   MAX(p.age) as age, 
                   MAX(n.region) as team,
                   MAX(n.noc) as noc,
                   STRING_AGG(DISTINCT e.sport, ', ') as sport, 
                   COUNT(DISTINCT g.game_name)::text as games,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
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
        if team:
            query += " AND n.region = %s"
            params.append(team)
        if game_filter:
            query += " AND g.game_name = %s"
            params.append(game_filter)
        if medals:
            query += " AND p.medal = ANY(%s::text[])"
            params.append(medals)
        if seasons:
            query += " AND g.season = ANY(%s::text[])"
            params.append(seasons)
        if sexes:
            query += " AND a.sex = ANY(%s::text[])"
            params.append(sexes)
        if year.isdigit():
            query += " AND g.year = %s"
            params.append(int(year))
        if sport:
            query += " AND e.sport ILIKE %s"
            params.append(f'%{sport}%')

        query += """
            GROUP BY a.athlete_id, a.name, a.sex
            ORDER BY gold ASC, silver ASC, bronze ASC, a.name ASC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        cur.execute(query, params)
        athletes_list = cur.fetchall()
        has_next = len(athletes_list) == limit
        
    except Exception as e:
        print(f"Error: {e}")
        athletes_list = []
        has_next = False
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
        
    return render_template('athletes.html', athletes=athletes_list, page=page, has_next=has_next)

@app.route('/athlete/<int:id>')
def athlete_detail(id):
    athlete_data = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        query = """
            SELECT a.athlete_id, a.name, a.sex, p.age, p.height, p.weight, n.region, e.sport, e.event_name, g.game_name, p.medal
            FROM Athletes a
            JOIN Participations p ON a.athlete_id = p.athlete_id
            JOIN Nations n ON p.noc = n.noc
            JOIN Games g ON p.game_id = g.game_id
            JOIN Events e ON p.event_id = e.event_id
            WHERE a.athlete_id = %s
            ORDER BY g.year ASC
        """
        cur.execute(query, (id,))
        athlete_data = cur.fetchall()
    except Exception:
        athlete_data = None
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
    return render_template('athlete_detail.html', details=athlete_data)

@app.route('/nation/<noc>')
def nation_detail(noc):
    nation_info = None
    nation_stats = None
    top_athletes = []
    details = []
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        cur.execute("SELECT region FROM Nations WHERE noc = %s", (noc,))
        nation_info = cur.fetchone()
        
        cur.execute("""
            SELECT
                COUNT(DISTINCT p.athlete_id) AS total_athletes,
                COUNT(DISTINCT p.game_id) AS total_editions,
                COUNT(DISTINCT e.sport) AS total_sports,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
            FROM Participations p
            JOIN Events e ON p.event_id = e.event_id
            WHERE p.noc = %s
        """, (noc,))
        nation_stats = cur.fetchone()
        
        cur.execute("""
            SELECT a.athlete_id, a.name, a.sex,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze,
                COUNT(p.medal) FILTER (WHERE p.medal IN ('Gold', 'Silver', 'Bronze')) AS total_medals
            FROM Participations p
            JOIN Athletes a ON p.athlete_id = a.athlete_id
            WHERE p.noc = %s
            GROUP BY a.athlete_id, a.name, a.sex
            ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
            LIMIT 3
        """, (noc,))
        top_athletes = cur.fetchall()
        
        cur.execute("""
            SELECT a.athlete_id as id, a.name, 
                   STRING_AGG(DISTINCT e.sport, ', ') as sport, 
                   COUNT(DISTINCT g.game_name)::text as game_name,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
            FROM Participations p
            JOIN Athletes a ON p.athlete_id = a.athlete_id
            JOIN Events e ON p.event_id = e.event_id
            JOIN Games g ON p.game_id = g.game_id
            WHERE p.noc = %s
            GROUP BY a.athlete_id, a.name
            ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
            OFFSET 3
        """, (noc,))
        details = cur.fetchall()
        
    except Exception:
        pass
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
        
    return render_template('nation_detail.html', nation_info=nation_info, nation_stats=nation_stats, top_athletes=top_athletes, details=details, noc=noc)

@app.route('/game/<path:game_name>')
def game_detail(game_name):
    game_info = None
    game_stats = None
    top_athletes = []
    details = []
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        cur.execute("SELECT city, season, year FROM Games WHERE game_name = %s", (game_name,))
        game_info = cur.fetchone()
        
        cur.execute("""
            SELECT
                COUNT(DISTINCT p.athlete_id) AS total_athletes,
                COUNT(DISTINCT p.noc) AS total_nations,
                COUNT(DISTINCT e.sport) AS total_sports,
                COUNT(DISTINCT p.event_id) AS total_events,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
            FROM Participations p
            JOIN Events e ON p.event_id = e.event_id
            JOIN Games g ON p.game_id = g.game_id
            WHERE g.game_name = %s
        """, (game_name,))
        game_stats = cur.fetchone()
        
        cur.execute("""
            SELECT a.athlete_id, a.name, n.region AS nation, a.sex,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
                COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze,
                COUNT(p.medal) FILTER (WHERE p.medal IN ('Gold', 'Silver', 'Bronze')) AS total_medals
            FROM Participations p
            JOIN Athletes a ON p.athlete_id = a.athlete_id
            JOIN Nations n ON p.noc = n.noc
            JOIN Games g ON p.game_id = g.game_id
            WHERE g.game_name = %s
            GROUP BY a.athlete_id, a.name, n.region, a.sex
            ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
            LIMIT 3
        """, (game_name,))
        top_athletes = cur.fetchall()
        
        cur.execute("""
            SELECT a.athlete_id as id, a.name, MAX(n.region) as region, 
                   STRING_AGG(DISTINCT e.sport, ', ') as sport,
                   STRING_AGG(DISTINCT e.event_name, ', ') as event_name,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
                   COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
            FROM Participations p
            JOIN Athletes a ON p.athlete_id = a.athlete_id
            JOIN Nations n ON p.noc = n.noc
            JOIN Events e ON p.event_id = e.event_id
            JOIN Games g ON p.game_id = g.game_id
            WHERE g.game_name = %s
            GROUP BY a.athlete_id, a.name
            ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
            LIMIT 500 OFFSET 3
        """, (game_name,))
        details = cur.fetchall()
        
    except Exception:
        pass
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
        
    return render_template('edition_detail.html', game_info=game_info, game_stats=game_stats, top_athletes=top_athletes, details=details, game_name=game_name)

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
    except Exception:
        nations_list = []
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
        
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
            query += " AND season = ANY(%s::text[])"
            params.append(seasons)
            
        query += " ORDER BY year DESC, season ASC"
        
        cur.execute(query, params)
        games_list = cur.fetchall()
    except Exception:
        games_list = []
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
        
    return render_template('games.html', games=games_list)

@app.route('/add_athlete', methods=['GET', 'POST'])
def add_athlete():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
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

            cur.execute("SELECT noc FROM Nations WHERE noc = %s", (noc,))
            if not cur.fetchone():
                cur.execute("INSERT INTO Nations (noc, region) VALUES (%s, %s)", (noc, team))

            cur.execute("SELECT game_id FROM Games WHERE game_name = %s", (games,))
            game_result = cur.fetchone()
            if game_result:
                game_id = game_result[0]
            else:
                cur.execute("SELECT COALESCE(MAX(game_id), 0) + 1 FROM Games")
                game_id = cur.fetchone()[0]
                cur.execute("INSERT INTO Games (game_id, game_name, year, season, city) VALUES (%s, %s, %s, %s, %s)",
                            (game_id, games, int(year), season, city))

            cur.execute("SELECT event_id FROM Events WHERE event_name = %s", (event_name,))
            event_result = cur.fetchone()
            if event_result:
                event_id = event_result[0]
            else:
                cur.execute("SELECT COALESCE(MAX(event_id), 0) + 1 FROM Events")
                event_id = cur.fetchone()[0]
                cur.execute("INSERT INTO Events (event_id, sport, event_name) VALUES (%s, %s, %s)",
                            (event_id, sport, event_name))

            cur.execute("SELECT COALESCE(MAX(athlete_id), 0) + 1 FROM Athletes")
            new_athlete_id = cur.fetchone()[0]
            cur.execute("INSERT INTO Athletes (athlete_id, name, sex) VALUES (%s, %s, %s)", 
                        (new_athlete_id, name, sex))

            cur.execute("""
                INSERT INTO Participations (athlete_id, game_id, event_id, noc, age, height, weight, medal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_athlete_id, game_id, event_id, noc, age, height, weight, medal))

            conn.commit()
            flash('Atleta e partecipazione registrati con successo.', 'success')
            return redirect(url_for('athletes'))
            
        except Exception:
            if conn: conn.rollback()
            flash("Errore durante l'inserimento.", 'danger')
        finally:
            if 'cur' in locals() and cur: cur.close()
            if 'conn' in locals() and conn: conn.close()
            
    return render_template('add_athlete.html')

@app.route('/delete_athlete/<int:id>', methods=['POST'])
def delete_athlete(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM Participations WHERE athlete_id = %s", (id,))
        cur.execute("DELETE FROM Athletes WHERE athlete_id = %s", (id,))
        
        conn.commit()
        flash('Record eliminato con successo.', 'success')
    except Exception:
        if conn: conn.rollback()
        flash("Errore durante l'eliminazione.", 'danger')
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()
    return redirect(url_for('athletes'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')