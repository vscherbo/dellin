CREATE OR REPLACE FUNCTION arc_energo.get_inn(in_code integer)
RETURNS text
LANGUAGE sql 
AS $function$ 
SELECT "ИНН" 
FROM "Предприятия" WHERE "Код" = in_code;
 $function$