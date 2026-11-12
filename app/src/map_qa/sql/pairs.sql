-- Photo-road candidates with distance recomputed in EPSG:2180 (ADR-002 §3.1-3.2).
-- Metric geometry columns carry the _2180 suffix; distance functions only take *_2180 columns (TAC-002-01).
CREATE OR REPLACE TABLE link_base AS
WITH base AS (
    SELECT
        l.photo_id,
        l.osm_way_id,
        l.overture_id,
        l.distance_m,
        l.bearing_diff,
        l.directed_bearing_diff,
        l.match_method,
        l.osm_candidate_count,
        coalesce(l.candidate_flags, '') AS candidate_flags_raw,
        p.heading,
        p.is_panorama,
        count(*) OVER (PARTITION BY p.longitude, p.latitude, p.captured_at) AS same_position_time_n,
        o.highway,
        o.access,
        o.motor_vehicle,
        o.bridge,
        o.tunnel,
        o.layer,
        len(coalesce(s.level_rules, [])) AS overture_level_rules_n,
        ST_Transform(ST_Point(p.longitude, p.latitude), 'EPSG:4326', 'EPSG:2180', always_xy := true) AS camera_2180,
        CASE WHEN o.osm_id IS NOT NULL
             THEN ST_Transform(o.geometry, 'EPSG:4326', 'EPSG:2180', always_xy := true) END AS road_2180
    FROM photo_road_links l
    JOIN photos p USING (photo_id)
    LEFT JOIN osm_roads o ON o.osm_id = l.osm_way_id
    LEFT JOIN overture_segments s ON s.id = l.overture_id
)
SELECT * EXCLUDE (camera_2180, road_2180),
       ST_Distance(camera_2180, road_2180) AS distance_m_recomputed
FROM base;
