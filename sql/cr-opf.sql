CREATE OR REPLACE FUNCTION arc_energo.opf(arc_energo."Предприятия")
 RETURNS character varying
 LANGUAGE sql
AS $function$
WITH dl_opf AS (
SELECT upper(opf_name) as opf_name FROM shp.dl_opf_list WHERE 
country_id = (SELECT c.country_id FROM shp.dl_countries c WHERE c.country_name = 'Россия')
AND juridical) 
    SELECT opf FROM 
    (
     SELECT upper(trim('''" ' FROM substring (regexp_replace("ЮрНазвание", '[)(]', '', 'g')
            from '^[[:space:]]*[а-яА-Я]+[ "'']+') )) as opf FROM "Предприятия"
     where "Предприятия"."Код" = $1."Код"
     UNION
     SELECT upper(trim('''" ' FROM substring (regexp_replace("ЮрНазвание", '[)(]', '', 'g')
            from '[ "'']+[а-яА-Я]+[[:space:]]*$') )) FROM "Предприятия"
    where "Предприятия"."Код" = $1."Код"
    ) o
    WHERE opf is NOT NULL and opf IN (SELECT * FROM dl_opf)
$function$
