SELECT 
    etsocmvc, 
    cgrocmvc, 
    decocmvc, 
    cptocmvc, 
    jrnocmvc, 
    pieocecr, 
    numocmvc, 
    ecrocmvc, 
    libocmvc,
    licocmvc,
    libocecr, 
    licocecr, 
    letocmvc,
    tieocmvc,
    nomoetie,
    pixocecr,
    sum(mtcocmvc) AS mtcocmvc,
    sum(mtdocmvc) AS mtdocmvc,
    sum(quoocmvc) AS quoocmvc
FROM ocmvc m
JOIN ocecr e on m.ecrocmvc = e.numocecr and etsocmvc = etsocecr
JOIN oecpt c on c.numoecpt  = m.cptocmvc and m.etsocmvc = c.etsoecpt
JOIN gtets t on t.numgtets = m.etsocmvc 
LEFT JOIN oetie o on m.tieocmvc = o.numoetie
WHERE 1=1
AND e.etaocecr = '{{filtres.etaocecr}}'
AND typocmvc NOT IN ('C1','C2')
AND left(etsocmvc,1) IN ('1','5')
AND left(cptocmvc,1) = '{{filtres.compte}}'
AND LEFT(decocmvc,4) = '{{filtres.annee}}'
AND jrnocmvc NOT IN ('ODCB','ODCP','ODCR','ODRM')
GROUP BY 
    etsocmvc,
    cgrocmvc,
    decocmvc,
    cptocmvc,
    jrnocmvc,
    pieocecr,
    numocmvc,
    ecrocmvc,
    libocmvc,
    licocmvc,
    libocecr,
    licocecr,
    letocmvc,
    tieocmvc,
    nomoetie,
    pixocecr
having (sum( mtcocmvc) - sum(mtdocmvc)) <> 0;