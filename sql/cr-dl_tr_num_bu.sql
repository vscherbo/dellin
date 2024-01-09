create trigger dl_tr_num_bu before update of tracking_code, shp_id on
shp.vs_dl_tracking for each row execute procedure save_dl_conflict();
