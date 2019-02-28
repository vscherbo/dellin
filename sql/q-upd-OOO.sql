-- 
UPDATE "Предприятия" SET "ЮрНазвание" = regexp_replace("ЮрНазвание", 'Общество с ограниченной ответственностью', 'ООО', 'gi')
-- SELECT "ЮрНазвание", regexp_replace("ЮрНазвание", 'Общество с ограниченной ответственностью', 'ООО', 'gi') FROM "Предприятия"
WHERE "Код" IN (
SELECT Код FROM (
WITH dl_opf AS (
SELECT opf_name FROM shp.dl_opf_list WHERE 
country_id = (SELECT c.country_id FROM shp.dl_countries c WHERE c.country_name = 'Россия')
AND juridical)
SELECT 
e."Код", e."ИНН", e."ДатаСоздания", p."ФИО", 
e."ЮрНазвание"
, regexp_replace(e."ЮрНазвание", 'Общество с ограниченной ответственностью', 'ООО', 'gi')
, e.opf 
FROM arc_energo."Предприятия" e
JOIN "Сотрудники" p ON p."Номер" = e."Создатель" 
WHERE 
e."ИНН" IS NOT NULL
AND e."ИНН" <> ''
AND (e.opf NOT IN (SELECT * FROM dl_opf) OR e.opf IS NULL)
AND e."ДатаСоздания" > '2016-01-01'
-- AND ФИО = 'auto_bill'
AND strpos(lower(e."ЮрНазвание"), 'общество с ограниченной ответственностью') > 0
) kod )