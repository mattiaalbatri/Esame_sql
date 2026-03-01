
SELECT
    (SELECT COUNT(*) FROM Athletes) AS total_athletes,
    (SELECT COUNT(*) FROM Nations) AS total_nations,
    (SELECT COUNT(*) FROM Games) AS total_editions,
    (SELECT COUNT(*) FROM Participations WHERE medal != 'NA') AS total_medals;


SELECT a.athlete_id as id, a.name, a.sex, p.age, n.region as team,
       e.sport, g.game_name as games, p.medal, n.noc
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Games g ON p.game_id = g.game_id
JOIN Events e ON p.event_id = e.event_id
JOIN Nations n ON p.noc = n.noc
WHERE n.region ILIKE '%Italy%' 
ORDER BY 
    CASE p.medal
        WHEN 'Gold' THEN 1
        WHEN 'Silver' THEN 2
        WHEN 'Bronze' THEN 3
        ELSE 4
    END ASC,
    a.name ASC
LIMIT 500 OFFSET 0;


SELECT a.name, a.sex, p.age, p.height, p.weight, n.region, 
       e.sport, e.event_name, g.game_name, p.medal
FROM Athletes a
JOIN Participations p ON a.athlete_id = p.athlete_id
JOIN Nations n ON p.noc = n.noc
JOIN Games g ON p.game_id = g.game_id
JOIN Events e ON p.event_id = e.event_id
WHERE a.athlete_id = 12345
ORDER BY g.year DESC;


SELECT a.name, e.sport, g.game_name, p.medal
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Events e ON p.event_id = e.event_id
JOIN Games g ON p.game_id = g.game_id
WHERE p.noc = 'ITA'
ORDER BY g.year DESC, a.name ASC;


SELECT a.name, n.region, e.sport, e.event_name, p.medal
FROM Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Nations n ON p.noc = n.noc
JOIN Events e ON p.event_id = e.event_id
JOIN Games g ON p.game_id = g.game_id
WHERE g.game_name = '2016 Summer'
ORDER BY e.sport ASC, a.name ASC;


SELECT noc AS code, region AS name FROM Nations ORDER BY region ASC;
SELECT year, season, game_name, city FROM Games ORDER BY year DESC, season ASC;


WITH nuovo_atleta AS (
    INSERT INTO Athletes (athlete_id, name, sex)
    VALUES (2000001, 'Mario Rossi', 'M')
    RETURNING athlete_id
),
info_gara AS (
    SELECT g.game_id, e.event_id
    FROM Games g, Events e
    WHERE g.game_name = '2016 Summer'
      AND e.event_name = 'Cycling Men''s Road Race, Individual'
)
INSERT INTO Participations (athlete_id, game_id, event_id, noc, age, height, weight, medal)
SELECT nuovo_atleta.athlete_id, info_gara.game_id, info_gara.event_id, 'ITA', 25, 180, 75.5, 'NA'
FROM nuovo_atleta, info_gara;


UPDATE Athletes SET name = 'Mario Rossi Jr.' WHERE athlete_id = 2000001;

DELETE FROM Participations WHERE athlete_id = 2000001;
DELETE FROM Athletes WHERE athlete_id = 2000001;