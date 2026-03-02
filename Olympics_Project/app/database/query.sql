
SELECT
    (SELECT COUNT(*) FROM Athletes) AS athletes,
    (SELECT COUNT(*) FROM Nations) AS nations,
    (SELECT COUNT(*) FROM Games) AS games,
    (SELECT COUNT(*) FROM Participations WHERE medal != 'NA') AS medals;

SELECT a.athlete_id as id, a.name, a.sex, 
       MAX(p.age) as age, 
       MAX(n.region) as team,
       MAX(n.noc) as noc,
       STRING_AGG(DISTINCT e.sport, ', ') as sport, 
       STRING_AGG(DISTINCT g.game_name, ', ') as games,
       COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
       COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
       COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Games g ON p.game_id = g.game_id
JOIN Events e ON p.event_id = e.event_id
JOIN Nations n ON p.noc = n.noc
WHERE 1=1 
GROUP BY a.athlete_id, a.name, a.sex
ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
LIMIT 500 OFFSET 0;

SELECT a.athlete_id, a.name, a.sex, p.age, p.height, p.weight, n.region, e.sport, e.event_name, g.game_name, p.medal,
       g.game_id, e.event_id
FROM Athletes a
JOIN Participations p ON a.athlete_id = p.athlete_id
JOIN Nations n ON p.noc = n.noc
JOIN Games g ON p.game_id = g.game_id
JOIN Events e ON p.event_id = e.event_id
WHERE a.athlete_id = 1 
ORDER BY g.year DESC;

SELECT noc AS code, region AS name FROM Nations ORDER BY region ASC;

SELECT
    COUNT(DISTINCT p.athlete_id) AS total_athletes,
    COUNT(DISTINCT p.game_id) AS total_editions,
    COUNT(DISTINCT e.sport) AS total_sports,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
FROM Participations p
JOIN Events e ON p.event_id = e.event_id
WHERE p.noc = 'ITA';

SELECT year, season, game_name, city FROM Games ORDER BY year DESC, season ASC;

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
WHERE g.game_name = '2012 Summer';

SELECT sport, COUNT(DISTINCT event_name) as total_events 
FROM Events 
GROUP BY sport 
ORDER BY sport ASC;

SELECT COALESCE(MAX(athlete_id), 0) + 1 FROM Athletes;
SELECT COALESCE(MAX(game_id), 0) + 1 FROM Games;
SELECT COALESCE(MAX(event_id), 0) + 1 FROM Events;

INSERT INTO Athletes (athlete_id, name, sex) VALUES (100000, 'Mario Rossi', 'M');

INSERT INTO Participations (athlete_id, game_id, event_id, noc, age, height, weight, medal)
VALUES (100000, 1, 1, 'ITA', 25, 180, 75, 'Gold');

UPDATE Participations 
SET age = 26, medal = 'Silver'
WHERE athlete_id = 100000 AND game_id = 1 AND event_id = 1;

DELETE FROM Participations WHERE athlete_id = 100000;
DELETE FROM Athletes WHERE athlete_id = 100000;