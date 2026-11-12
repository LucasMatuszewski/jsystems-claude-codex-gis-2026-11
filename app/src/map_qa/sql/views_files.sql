-- FilesSource views (ADR-001 §3.2). Placeholders are quoted absolute path literals.
-- Label files (reference_labels.csv, signs/labels.csv) are deliberately NOT registered (ADR-003 TAC-003-03).
CREATE OR REPLACE VIEW osm_roads AS SELECT * FROM read_parquet({osm_roads});
CREATE OR REPLACE VIEW overture_segments AS SELECT * FROM read_parquet({overture_segments});
CREATE OR REPLACE VIEW photos AS SELECT * FROM read_csv({photos});
CREATE OR REPLACE VIEW photo_road_links AS SELECT * FROM read_csv({photo_road_links});
CREATE OR REPLACE VIEW signs AS SELECT * FROM read_csv({signs});
CREATE OR REPLACE VIEW signs_nearest_osm AS SELECT * FROM read_csv({signs_nearest_osm},
    types = {{'maxspeed': 'VARCHAR', 'maxspeed_forward': 'VARCHAR', 'maxspeed_backward': 'VARCHAR',
              'maxspeed_conditional': 'VARCHAR'}});
