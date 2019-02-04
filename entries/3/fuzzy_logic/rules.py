Function-Block "invasion_opportunity"
Antecedent: game_turn, range := (0 .. 200)
            terms: ['early', 'mid', 'late']
Antecedent: distance, range := (0.0 .. 1.0)
            terms: ['close', 'moderate', 'far']
Antecedent: ships_surplus, range := (-10.0 .. 10.0)
            terms: ['deficit', 'even', 'surplus']
Antecedent: planet_size, range := (0 .. 16)
            terms: ['puny', 'small', 'medium', 'large', 'huge']
Consequent: opportunity, range := (0.0 .. 0.999)
            terms: ['bad', 'mediocre', 'good']
Rule No1.1: IF game_turn[early] AND ((ships_surplus[deficit] OR distance[far]) OR planet_size[puny]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.2: IF (game_turn[early] AND distance[moderate]) AND (planet_size[small] OR planet_size[puny]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.3: IF (game_turn[early] AND distance[moderate]) AND (planet_size[medium] OR planet_size[large]) THEN opportunity[mediocre]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.4: IF (game_turn[early] AND distance[moderate]) AND planet_size[huge] THEN opportunity[mediocre]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.5: IF (game_turn[late] AND (planet_size[small] OR planet_size[medium])) AND (ships_surplus[deficit] OR distance[far]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.6: IF (((game_turn[mid] OR game_turn[late]) AND ships_surplus[deficit]) AND distance[far]) AND (planet_size[puny] OR planet_size[small]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.7: IF (((game_turn[mid] OR game_turn[late]) AND ships_surplus[even]) AND distance[moderate]) AND (planet_size[puny] OR planet_size[small]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.8: IF ships_surplus[even] AND (distance[moderate] OR planet_size[small]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.9: IF ships_surplus[even] AND (distance[far] AND planet_size[puny]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.10: IF (game_turn[mid] OR game_turn[late]) AND ((ships_surplus[deficit] OR distance[far]) OR planet_size[puny]) THEN opportunity[bad]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.11: IF ((game_turn[late] AND (planet_size[small] OR planet_size[medium])) AND ships_surplus[even]) AND (distance[far] OR distance[moderate]) THEN opportunity[mediocre]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.12: IF ((game_turn[late] AND (planet_size[small] OR planet_size[medium])) AND ships_surplus[surplus]) AND distance[close] THEN opportunity[good]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.13: IF (game_turn[late] AND (planet_size[large] OR planet_size[huge])) AND (ships_surplus[even] OR ships_surplus[surplus]) THEN opportunity[good]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.14: IF (((game_turn[mid] OR game_turn[early]) AND (((planet_size[large] OR planet_size[huge]) OR planet_size[medium]) OR planet_size[small])) AND (ships_surplus[even] OR ships_surplus[surplus])) AND (distance[far] OR distance[moderate]) THEN opportunity[good]
	AND aggregation function : fmin
	OR aggregation function  : fmax
Rule No1.15: IF game_turn[mid] OR (((game_turn[early] AND (((planet_size[large] OR planet_size[huge]) OR planet_size[medium]) OR planet_size[small])) AND (ships_surplus[even] OR ships_surplus[surplus])) AND (distance[far] OR distance[moderate])) THEN opportunity[good]
	AND aggregation function : fmin
	OR aggregation function  : fmax

