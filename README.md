<div align="center">

# OLYMPICS DATABASE MANAGER

**120 anni di storia olimpica in un database relazionale.**

`PostgreSQL 15` · `Flask` · `Docker` · `Python 3.10`

</div>

### Indice

- [Panoramica](#panoramica)
- [Architettura Docker](#architettura-docker)
- [Schema del Database](#schema-del-database)
- [Avvio Rapido](#avvio-rapido)
- [Struttura del Progetto](#struttura-del-progetto)
- [Funzionalita](#funzionalita)

---

## Panoramica

Applicazione web full-stack che carica il dataset [120 years of Olympic history](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) in un database **PostgreSQL** normalizzato, esponendolo attraverso un'interfaccia Flask containerizzata con Docker.

| | |
|:---|:---|
| Atleti registrati | ~135.000 |
| Partecipazioni censite | ~271.000 |
| Nazioni rappresentate | ~230 |
| Edizioni olimpiche | 51 |

L'interfaccia permette di consultare, filtrare, aggiungere, modificare ed eliminare atleti e partecipazioni — CRUD completo con ricerca parametrica e medaglieri aggregati.

---

## Architettura Docker

Due container orchestrati con **Docker Compose**: il database e l'applicazione web.

| Servizio | Immagine | Porta | Ruolo |
|:---|:---|:---|:---|
| `db` | `postgres:15` | 5432 | Database PostgreSQL con il database `olympics_db` |
| `web` | Build dal Dockerfile | 5000 | Applicazione Flask con connessione al database |

Il servizio `web` dipende da `db` tramite `depends_on`, garantendo l'avvio corretto del database prima dell'applicazione. I volumi montano il codice sorgente per lo sviluppo live.

Il **Dockerfile** parte da `python:3.10-slim`, installa le librerie di sistema per PostgreSQL (`libpq-dev`, `gcc`), copia le dipendenze Python e avvia l'applicazione Flask.

> Le variabili d'ambiente (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`) collegano automaticamente i due container senza configurazione manuale.

---

## Schema del Database

Struttura normalizzata in **5 tabelle** con integrita referenziale completa.

### Tabelle

| Tabella | PK | Colonne principali | Ruolo |
|:---|:---|:---|:---|
| **Nations** | `noc` | region, notes | Anagrafica nazioni (codice NOC a 3 caratteri) |
| **Athletes** | `athlete_id` | name, sex | Anagrafica atleti con vincolo CHECK su sex (M/F) |
| **Games** | `game_id` | game_name, year, season, city | Edizioni olimpiche con vincolo CHECK su season |
| **Events** | `event_id` | sport, event_name | Catalogo eventi sportivi con UNIQUE su event_name |
| **Participations** | `participation_id` | athlete_id, game_id, event_id, noc, age, height, weight, medal | Tabella centrale con 4 FK e CHECK su medal |

### Relazioni

La tabella **Participations** e il cuore dello schema. Collega le altre 4 tabelle tramite chiavi esterne:

| Foreign Key | Da | A |
|:---|:---|:---|
| `fk_athlete` | Participations.athlete_id | Athletes.athlete_id |
| `fk_game` | Participations.game_id | Games.game_id |
| `fk_event` | Participations.event_id | Events.event_id |
| `fk_noc` | Participations.noc | Nations.noc |

### Vincoli

| Tipo | Dettaglio |
|:---|:---|
| `CHECK` | Valori ammessi per `sex` (M, F), `season` (Summer, Winter), `medal` (Gold, Silver, Bronze, NA) |
| `SERIAL` | Generazione automatica degli ID progressivi |
| `UNIQUE` | Unicita garantita su `game_name` e `event_name` |
| `NOT NULL` | Campi obbligatori su name, game_name e tutte le FK |

> Il DDL completo si trova in `app/database/Create_table.sql`. Le query SQL sono in `app/database/query.sql` e `app/database/Analytical_query.sql`.

---

## Avvio Rapido

### Prerequisiti

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)

### Procedura

1. **Clona il repository** e posizionati nella cartella del progetto
2. **Avvia i container** con `docker-compose up --build` — questo crea il database PostgreSQL e l'applicazione Flask
3. **Carica i dati** eseguendo load_data.py` in un secondo terminale — lo script normalizza i CSV e li carica nelle 5 tabelle tramite una singola transazione
4. **Apri l'applicazione** su [http://localhost:5000](http://localhost:5000)

---

## Struttura del Progetto

| Percorso | Descrizione |
|:---|:---|
| `docker-compose.yml` | Orchestrazione dei due servizi (db + web) |
| `Dockerfile` | Build dell'immagine Flask |
| `requirements.txt` | Dipendenze Python (Flask, psycopg, Pandas, SQLAlchemy) |
| `data/athlete_events.csv` | Dataset principale (~271k righe) |
| `data/noc_regions.csv` | Mapping codici NOC alle nazioni |
| `app/app.py` | Applicazione Flask — routes e query |
| `app/database/Create_table.sql` | DDL dello schema del database |
| `app/database/query.sql` | Query CRUD utilizzate dall'applicazione |
| `app/database/Analytical_query.sql` | Query analitica per il medagliere |
| `app/database/load_data.py` | Script ETL per il caricamento dei CSV in PostgreSQL |
| `app/templates/` | Template HTML con Jinja2 |
| `app/static/` | Fogli di stile CSS e immagini |

---

## Funzionalita

| Sezione | Descrizione |
|:---|:---|
| Dashboard | Statistiche generali — atleti, nazioni, edizioni, medaglie totali |
| Atleti | Lista paginata con filtri combinabili per nome, nazione, sport, anno, sesso, medaglia |
| Dettaglio Atleta | Storico partecipazioni con modifica inline ed eliminazione |
| Nazioni | Elenco con ricerca, dettaglio per nazione con statistiche e top 3 atleti |
| Edizioni | Lista cronologica delle Olimpiadi con dettaglio per edizione |
| Sport | Catalogo discipline con conteggio eventi e dettaglio per sport |
| Aggiungi Atleta | Form per registrare un nuovo atleta con la sua prima partecipazione |

---

<div align="center">

MIT License

</div>
