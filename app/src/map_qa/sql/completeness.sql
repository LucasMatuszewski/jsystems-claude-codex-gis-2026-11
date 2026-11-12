-- Attribute completeness (ADR-001 §3.5): with_value / total for all roads and for photo-linked roads.
-- Requires views osm_roads, overture_segments and pairs.
WITH osm AS (
    SELECT
        osm_id,
        osm_id IN (SELECT osm_way_id FROM pairs) AS linked,
        len(list_filter(coalesce(json_keys(tags), []), k -> starts_with(k, 'maxspeed'))) > 0 AS has_maxspeed,
        nullif(trim(surface), '') IS NOT NULL AS has_surface,
        nullif(trim(lit), '') IS NOT NULL AS has_lit,
        (nullif(trim(lanes), '') IS NOT NULL
            OR json_extract_string(tags, '$."lanes:forward"') IS NOT NULL
            OR json_extract_string(tags, '$."lanes:backward"') IS NOT NULL) AS has_lanes,
        (nullif(trim(sidewalk), '') IS NOT NULL OR nullif(trim("sidewalk:left"), '') IS NOT NULL
            OR nullif(trim("sidewalk:right"), '') IS NOT NULL
            OR json_extract_string(tags, '$."sidewalk:both"') IS NOT NULL) AS has_sidewalk
    FROM osm_roads
),
ov AS (
    SELECT
        id IN (SELECT overture_id FROM pairs WHERE overture_id IS NOT NULL) AS linked,
        len(coalesce(speed_limits, [])) > 0 AS has_speed,
        len(coalesce(road_surface, [])) > 0 AS has_surface
    FROM overture_segments
),
osm_long AS (
    SELECT 'osm' AS source, a.attribute, p.population,
           count(*) FILTER (WHERE a.v) AS with_value, count(*) AS total
    FROM osm,
         LATERAL (VALUES ('maxspeed*', has_maxspeed), ('surface', has_surface), ('lit', has_lit),
                         ('lanes', has_lanes), ('sidewalk*', has_sidewalk)) a(attribute, v),
         LATERAL (SELECT 'all' AS population UNION ALL SELECT 'linked' WHERE osm.linked) p
    GROUP BY ALL
),
ov_long AS (
    SELECT 'overture' AS source, a.attribute, p.population,
           count(*) FILTER (WHERE a.v) AS with_value, count(*) AS total
    FROM ov,
         LATERAL (VALUES ('speed_limits', has_speed), ('road_surface', has_surface)) a(attribute, v),
         LATERAL (SELECT 'all' AS population UNION ALL SELECT 'linked' WHERE ov.linked) p
    GROUP BY ALL
)
SELECT source, attribute, population, with_value, total, 100.0 * with_value / total AS pct
FROM (SELECT * FROM osm_long UNION ALL SELECT * FROM ov_long)
ORDER BY source DESC, attribute, population;
