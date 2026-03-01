SELECT 
    a.name AS Atleta,
    n.region AS Nazione,
    g.year AS Anno,
    g.season AS Stagione,
    e.sport AS Sport,
    e.event_name AS Gara,
    p.medal AS Medaglia
FROM 
    Participations p
JOIN Athletes a ON p.athlete_id = a.athlete_id
JOIN Nations n ON p.noc = n.noc
JOIN Games g ON p.game_id = g.game_id
JOIN Events e ON p.event_id = e.event_id
WHERE 
    n.region = 'Italy'              
    AND p.medal = 'Gold'            
    AND g.season = 'Summer'         
    AND e.sport = 'Cycling'         
    AND g.year = 2016               
    AND a.sex = 'M'                
ORDER BY 
    a.name ASC;


SELECT 
    n.region AS Nazione,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS Ori,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS Argenti,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS Bronzi,
    COUNT(p.medal) FILTER (WHERE p.medal IN ('Gold', 'Silver', 'Bronze')) AS Totale_Medaglie
FROM Participations p
JOIN Nations n ON p.noc = n.noc
GROUP BY n.region
ORDER BY Ori DESC, Argenti DESC, Bronzi DESC;


SELECT noc AS code, region AS name 
FROM Nations 
ORDER BY region ASC;


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
SELECT 
    nuovo_atleta.athlete_id, 
    info_gara.game_id, 
    info_gara.event_id, 
    'ITA', 25, 180, 75.5, 'NA'
FROM nuovo_atleta, info_gara;


UPDATE Athletes 
SET name = 'Mario Rossi Jr.' 
WHERE athlete_id = 2000001;


DELETE FROM Participations WHERE athlete_id = 2000001;
DELETE FROM Athletes WHERE athlete_id = 2000001;