CREATE OR REPLACE VIEW arc_energo.vw_dl_shipping AS
 SELECT format('%s-%s-%s'::text, date_part('year'::text, 'now'::text::date), "substring"(b."инфо"::text, '[0-9]+\.([0-9]+){1}'::text), "substring"(b."инфо"::text, '([0-9]+){1}\.[0-9]+'::text)) AS dl_dt,
    f."Ф_ИНН" AS dl_sender,
    c."ИНН" AS dl_receiver,
    c."Код" AS receiver_code,
    b."№ счета"
   FROM "Счета" b
     JOIN "Предприятия" c ON b."Код" = c."Код"
     JOIN "Фирма" f ON f."КлючФирмы" = b."фирма"
  WHERE b."№ счета" NOT IN (SELECT excl_bill_no FROM shp.vs_dl_exclusion)
        AND (b."№ счета" NOT IN ( SELECT vw_splitted_bill."предок"
           FROM vw_splitted_bill))
        AND b."инфо"::text ~ similar_escape('%Забрал%.*[0-9].[0-9]+%отметил%'::text, NULL::text) 
        AND b."ОтгрузкаКем"::text ~~* '%лини%'::text AND b."Дата счета" >= '2018-02-01 00:00:00'::timestamp without time zone AND b."ДокТК" IS NULL;
