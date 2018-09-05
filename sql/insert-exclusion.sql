insert into shp.vs_dl_exclusion(excl_bill_no) 
select "№ счета" from arc_energo.vw_dl_shipping
where dl_dt::date < now()::date 