CREATE TABLE Nations (
    noc VARCHAR(3) PRIMARY KEY,
    region VARCHAR(255),
    notes TEXT
);

CREATE TABLE Athletes (
    athlete_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sex CHAR(1) CHECK (sex IN ('M', 'F'))
);

CREATE TABLE Games (
    game_id SERIAL PRIMARY KEY,
    game_name VARCHAR(255) UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    season VARCHAR(10) CHECK (season IN ('Summer', 'Winter')),
    city VARCHAR(255)
);

CREATE TABLE Events (
    event_id SERIAL PRIMARY KEY,
    sport VARCHAR(255) NOT NULL,
    event_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Participations (
    participation_id SERIAL PRIMARY KEY,
    athlete_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    noc VARCHAR(3) NOT NULL,
    age INTEGER,
    height INTEGER,
    weight NUMERIC(5,2),
    medal VARCHAR(10) DEFAULT 'None' CHECK (medal IN ('Gold', 'Silver', 'Bronze', 'NA')),
   
    CONSTRAINT fk_athlete FOREIGN KEY (athlete_id) REFERENCES Athletes(athlete_id),
    CONSTRAINT fk_game FOREIGN KEY (game_id) REFERENCES Games(game_id),
    CONSTRAINT fk_event FOREIGN KEY (event_id) REFERENCES Events(event_id),
    CONSTRAINT fk_noc FOREIGN KEY (noc) REFERENCES Nations(noc)
);