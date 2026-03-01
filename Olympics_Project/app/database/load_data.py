import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://user:password@localhost:5432/olympics_db"
engine = create_engine(DB_URL)

def run_ingestion():
    print("Avvio del processo di preparazione e caricamento dati...")

    try:
        df_main = pd.read_csv('data/athlete_events.csv')
        df_regions = pd.read_csv('data/noc_regions.csv')
    except FileNotFoundError:
        print("Errore: Impossibile trovare i file CSV. Assicurarsi che siano presenti nella cartella 'data/'.")
        return

    print("Elaborazione e normalizzazione dei dati in corso...")

    df_main['Medal'] = df_main['Medal'].fillna('NA')

    unique_nocs = pd.DataFrame({'noc': df_main['NOC'].unique()})
    nations = unique_nocs.merge(df_regions, how='left', left_on='noc', right_on='NOC')
    nations = nations[['noc', 'region', 'notes']]

    athletes = df_main[['ID', 'Name', 'Sex']].drop_duplicates(subset=['ID'])
    athletes.columns = ['athlete_id', 'name', 'sex']

    games = df_main[['Games', 'Year', 'Season', 'City']].drop_duplicates(subset=['Games'])
    games.columns = ['game_name', 'year', 'season', 'city']
    games['game_id'] = range(1, len(games) + 1)

    events = df_main[['Sport', 'Event']].drop_duplicates(subset=['Event'])
    events.columns = ['sport', 'event_name']
    events['event_id'] = range(1, len(events) + 1)

    part_temp = df_main.merge(games[['game_name', 'game_id']], left_on='Games', right_on='game_name')
    part_temp = part_temp.merge(events[['event_name', 'event_id']], left_on='Event', right_on='event_name')
    
    participations = part_temp[['ID', 'game_id', 'event_id', 'NOC', 'Age', 'Height', 'Weight', 'Medal']]
    participations.columns = ['athlete_id', 'game_id', 'event_id', 'noc', 'age', 'height', 'weight', 'medal']

    print("Inizio l'inserimento dei dati nel database. L'operazione richiedera' alcuni minuti...")

    try:
        with engine.begin() as connection:
            nations.to_sql('nations', con=connection, if_exists='append', index=False)
            print("Caricamento tabella 'nations' completato.")

            athletes.to_sql('athletes', con=connection, if_exists='append', index=False)
            print("Caricamento tabella 'athletes' completato.")

            games.to_sql('games', con=connection, if_exists='append', index=False)
            print("Caricamento tabella 'games' completato.")

            events.to_sql('events', con=connection, if_exists='append', index=False)
            print("Caricamento tabella 'events' completato.")

            participations.to_sql('participations', con=connection, if_exists='append', index=False)
            print("Caricamento tabella 'participations' completato.")

        print("Processo terminato con successo. La transazione e' stata confermata (COMMIT).")

    except Exception as e:
        print(f"Si e' verificato un errore critico durante l'inserimento: {e}")
        print("La transazione e' stata annullata. Nessun dato e' stato salvato.")

if __name__ == "__main__":
    run_ingestion()