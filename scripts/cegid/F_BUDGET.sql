Select 
etsobbud,
intgtets,
cgrobbud,
moiobbud,
posobbud,
sum(mtcobbud)as mtcobbud,
sum(mtdobbud) as mtdobbud
from obbud b
join gtets t on t.numgtets = b.etsobbud 
where etaobbud = 'A' 
and butobbud = 'BA'
and LEFT(moiobbud,4) = '{{filtres.annee}}' 
group by 
etsobbud,
intgtets,
cgrobbud,
moiobbud,
posobbud
;
