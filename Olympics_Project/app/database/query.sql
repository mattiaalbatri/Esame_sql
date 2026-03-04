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

SELECT region FROM Nations WHERE noc = 'ITA';

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

SELECT a.athlete_id, a.name, a.sex,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze,
    COUNT(p.medal) FILTER (WHERE p.medal IN ('Gold', 'Silver', 'Bronze')) AS total_medals
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
WHERE p.noc = 'ITA'
GROUP BY a.athlete_id, a.name, a.sex
ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
LIMIT 3;

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
WHERE p.noc = 'ITA'
GROUP BY a.athlete_id, a.name
ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
OFFSET 3;

SELECT city, season, year FROM Games WHERE game_name = '2016 Summer';

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
WHERE g.game_name = '2016 Summer';

SELECT a.athlete_id, a.name, n.region AS nation, a.sex,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze,
    COUNT(p.medal) FILTER (WHERE p.medal IN ('Gold', 'Silver', 'Bronze')) AS total_medals
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Nations n ON p.noc = n.noc
JOIN Games g ON p.game_id = g.game_id
WHERE g.game_name = '2016 Summer'
GROUP BY a.athlete_id, a.name, n.region, a.sex
ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
LIMIT 3;

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
WHERE g.game_name = '2016 Summer'
GROUP BY a.athlete_id, a.name
ORDER BY gold DESC, silver DESC, bronze DESC, a.name ASC
LIMIT 500 OFFSET 3;

SELECT
    COUNT(DISTINCT p.athlete_id) AS total_athletes,
    COUNT(DISTINCT p.noc) AS total_nations,
    COUNT(DISTINCT e.event_id) AS total_events,
    COUNT(DISTINCT p.game_id) AS total_editions,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
FROM Participations p
JOIN Events e ON p.event_id = e.event_id
WHERE e.sport = 'Athletics';

SELECT a.athlete_id, a.name, MAX(n.region) AS nation, a.sex,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze,
    COUNT(p.medal) FILTER (WHERE p.medal IN ('Gold', 'Silver', 'Bronze')) AS total_medals
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Nations n ON p.noc = n.noc
JOIN Events e ON p.event_id = e.event_id
WHERE e.sport = 'Athletics' AND p.medal IN ('Gold', 'Silver', 'Bronze')
GROUP BY a.athlete_id, a.name, a.sex
ORDER BY total_medals DESC, gold DESC, silver DESC, bronze DESC
LIMIT 3;

SELECT a.athlete_id, a.name, MAX(n.region) as region, 
        MAX(g.game_name) as game_name, MAX(e.event_name) as event_name,
        COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS gold,
        COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS silver,
        COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS bronze
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Nations n ON p.noc = n.noc
JOIN Events e ON p.event_id = e.event_id
JOIN Games g ON p.game_id = g.game_id
WHERE e.sport = 'Athletics'
GROUP BY a.athlete_id, a.name, g.game_id, e.event_id
ORDER BY g.year DESC, a.name ASC
LIMIT 500;

SELECT noc AS code, region AS name FROM Nations WHERE 1=1 ORDER BY region ASC;

SELECT year, season, game_name, city FROM Games WHERE 1=1 ORDER BY year DESC, season ASC;

SELECT sport, COUNT(DISTINCT event_name) as total_events FROM Events WHERE 1=1 GROUP BY sport ORDER BY sport ASC;

SELECT noc, region FROM Nations ORDER BY region ASC;
SELECT game_id, game_name, city FROM Games ORDER BY year DESC, season ASC;
SELECT event_id, sport, event_name FROM Events ORDER BY sport ASC, event_name ASC;

SELECT a.name, g.game_name, e.event_name, e.sport, 
        p.age, p.height, p.weight, p.medal, 
        p.noc, n.region as team
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Games g ON p.game_id = g.game_id
JOIN Events e ON p.event_id = e.event_id
JOIN Nations n ON p.noc = n.noc
WHERE p.athlete_id = 1 AND p.game_id = 1 AND p.event_id = 1;

SELECT COALESCE(MAX(athlete_id), 0) + 1 FROM Athletes;

INSERT INTO Athletes (athlete_id, name, sex) VALUES (2000001, 'Mario Rossi', 'M');

INSERT INTO Participations (athlete_id, game_id, event_id, noc, age, height, weight, medal)
VALUES (2000001, 1, 1, 'ITA', 25, 180, 75.5, 'Gold');

UPDATE Participations 
SET age = 26, height = 180, weight = 77.0, medal = 'Gold',
    noc = 'ITA', event_id = 2
WHERE athlete_id = 1 AND game_id = 1 AND event_id = 1;

DELETE FROM Participations WHERE athlete_id = 2000001;
DELETE FROM Athletes WHERE athlete_id = 2000001;
