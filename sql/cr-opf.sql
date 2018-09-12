CREATE OR REPLACE FUNCTION arc_energo.opf(arc_energo."Предприятия")
 RETURNS character varying
 LANGUAGE sql
AS $function$
    SELECT trim( substring ("ЮрНазвание" from '^[а-яА-Я]+ ') ) FROM "Предприятия" where $1."Код" = "Предприятия"."Код" 
$function$
