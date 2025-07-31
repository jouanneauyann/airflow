SELECT distinct
	etsocmvc+'/ZZZZ/'+ left(cgrocmvc,2)+'/'+ right(left(cgrocmvc,6),4) as ECR_CODANA,
	etsocmvc+'/'+ left(cgrocmvc,2)+'/'+ right(left(cgrocmvc,6),4) as ECR_CODANA_F,
	F.etsoecgr as ANA_CODE1,
	intgtets as Lib_ANA_CODE1,
	F.intoecgr as Lib_ANA_CODE3,
	F.numoecgr as ANA_CODE3,
	M.intoecgr as Lib_ANA_CODE4,
	M.numoecgr as ANA_CODE4
from ocmvc m , oecgr F, oecgr M, ocecr e, gtets t
where 1= 1
	and F.etsoecgr = etsocmvc 
    and left(cgrocmvc,2) = F.numoecgr 
	and right(left(cgrocmvc,6),4) = M.numoecgr 
	and M.etsoecgr = etsocmvc
	and t.numgtets = m.etsocmvc 
	and m.ecrocmvc = e.numocecr and etsocmvc = etsocecr
	and e.etaocecr = 'V' 
	and left(cptocmvc,1) in ( '6','7') 
	and decocmvc >= 20230101 
	and (etsocmvc like '1%' or etsocmvc='569001');