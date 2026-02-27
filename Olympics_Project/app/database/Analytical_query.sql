SELECT 
    n.region AS Nazione,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Gold') AS Oro,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Silver') AS Argento,
    COUNT(p.medal) FILTER (WHERE p.medal = 'Bronze') AS Bronzo,
    COUNT(p.medal) AS Totale_Medaglie
FROM 
    Participations p
JOIN 
    Nations n ON p.noc = n.noc
JOIN 
    Games g ON p.game_id = g.game_id
WHERE 
    p.medal IN ('Gold', 'Silver', 'Bronze')
    AND g.season = 'Summer'
GROUP BY 
    n.region
ORDER BY 
    Oro DESC, 
    Argento DESC, 
    Bronzo DESC
LIMIT 20;