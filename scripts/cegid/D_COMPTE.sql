SELECT DISTINCT
    numoecpt,
    intoecpt
FROM
    oecpt
WHERE
    etsoecpt = '{{ filtres.structure }}';