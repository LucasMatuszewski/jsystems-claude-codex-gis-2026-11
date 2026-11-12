# Map QA input data profile

Profile of the Kraków map QA inputs in `course-materials/exercise-data/map-qa/`, prepared before the ADRs and the implementation plan. Read-only: no input file or Databricks object was changed, and no paid API was called.

## 1. Commands and versions

| Item | Value |
|---|---|
| Date | 2026-11-12 |
| OS | Windows 11 (10.0.26200) |
| uv | 0.13.7 |
| Python | 3.12.16 (downloaded by `uv run --python 3.12`) |
| DuckDB | 1.5.6 + `spatial` extension (pinned in `profile_data.py`) |
| Databricks CLI | v1.26.0 (`sources.json` records verification with 1.23.0) |
| Databricks transport | SQL Statement Execution REST API 2.0 via `query_databricks.py` |

Commands:

```powershell
# 1. Bundled profile (profile.sql) - local files
uv run --python 3.12 course-materials/exercise-data/map-qa/profile_data.py

# 2. One Databricks read (SELECT only)
uv run --python 3.12 course-materials/exercise-data/map-qa/query_databricks.py --statement "SELECT 'osm_roads' AS source, count(*) AS rows FROM workspace.map_qa.osm_roads UNION ALL SELECT 'overture_segments', count(*) FROM workspace.map_qa.overture_segments UNION ALL SELECT 'photos', count(*) FROM workspace.map_qa.photos UNION ALL SELECT 'photo_road_links', count(*) FROM workspace.map_qa.photo_road_links UNION ALL SELECT 'traffic_signs', count(*) FROM workspace.map_qa.traffic_signs"
```

Notes:

- **Windows encoding:** without `PYTHONUTF8=1`, `profile_data.py` crashes with `UnicodeEncodeError` (cp1250 console vs DuckDB box-drawing characters). All runs used `PYTHONUTF8=1`.
- **Extra checks:** duplicates, keys, `maxspeed` formats and `traffic_signs` were profiled with additional read-only DuckDB queries kept outside the repository. They are not part of `profile.sql`.
- **Credentials:** `DATABRICKS_HOST`, `DATABRICKS_TOKEN` and `DATABRICKS_SQL_WAREHOUSE_ID` were checked for presence only (all set). Values were never printed.

## 2. Row counts: local files vs Databricks

| Table | Local file | Local rows | Databricks `workspace.map_qa.*` | Match |
|---|---|---:|---:|---|
| osm_roads | `osm_roads.parquet` | 99,768 | 99,768 | ✅ |
| overture_segments | `overture_segments.parquet` | 85,405 | 85,405 | ✅ |
| photos | `photos.csv` | 561 | 561 | ✅ |
| photo_road_links | `photo_road_links.csv` | 561 | 561 | ✅ |
| traffic_signs | `traffic_signs.geojson` | 1,730 | 1,730 | ✅ |
| reference_labels | `reference_labels.csv` | 320 (100 photos) | – (not in Databricks) | – |

Databricks statement state: `SUCCEEDED`, 5 rows, not truncated. Matching counts mean the snapshots are the same size. They do not prove the contents are identical: no hashes or column checksums were compared.

## 3. Schemas and types

### `osm_roads.parquet` (26 columns)

`osm_id` BIGINT, `osm_version` BIGINT, `osm_timestamp` **VARCHAR**, `node_ids` BIGINT[], `start_node`/`end_node` BIGINT, `boundary_crossing` BOOLEAN, `tags` **VARCHAR (JSON text)**, extracted tag columns as VARCHAR (`highway`, `maxspeed`, `surface`, `lanes`, `oneway`, `lit`, `sidewalk`, `sidewalk:left`, `sidewalk:right`, `junction`, `ref`, `name`, `access`, `motor_vehicle`, `bridge`, `tunnel`, `layer`), `geometry` GEOMETRY('EPSG:4326').

- `maxspeed` and `lanes` are **strings**, not numbers. Parsing is the pipeline's responsibility.
- Every tag that is not extracted (`maxspeed:forward`, `source:maxspeed`, …) exists only inside the `tags` JSON.

### `overture_segments.parquet` (14 columns)

`id` VARCHAR (GERS), `geometry` GEOMETRY('OGC:CRS84'), `class`, `subclass`, `name`, `version` INTEGER, `bbox` STRUCT, and nested lists of structs: `sources`, `connectors`, `speed_limits`, `road_surface`, `road_flags`, `access_restrictions`, `level_rules`.

`speed_limits` element: `min_speed{value,unit}`, `max_speed{value,unit}`, `is_max_speed_variable`, `when{during, heading, using[], recognized[], mode[], vehicle[]}`, `between DOUBLE[]` (linear referencing 0–1 along the segment).

### `photos.csv` (21 columns)

`photo_id`, `filename`, `source`, `url`, `source_url`, `longitude`/`latitude` DOUBLE, `heading` DOUBLE, `captured_at` TIMESTAMPTZ, `sequence`, `license`, `license_url`, `author`, `source_sha256`, `sha256`, `bytes`, `transformation`, `horizontal_accuracy_m` DOUBLE, `is_panorama` BOOLEAN, `width`, `height`.

### `photo_road_links.csv` (11 columns)

`photo_id`, `osm_way_id` BIGINT, `overture_id` VARCHAR, `distance_m`, `way_bearing`, `bearing_diff`, `directed_bearing_diff`, `overture_distance_m` DOUBLE, `osm_candidate_count` BIGINT, `match_method`, `candidate_flags` (`;`-separated VARCHAR).

### `traffic_signs.geojson` (POINT, 1,730 rows)

`id`, `object_value` (e.g. `regulatory--maximum-speed-limit-70--g1`), `object_type`, `first_seen_at`/`last_seen_at` TIMESTAMPTZ, `source`, `license`, `source_url`, `image_ids` VARCHAR[], `geom` GEOMETRY('EPSG:4326').

### `reference_labels.csv`

`photo_id`, `question`, `label`, `status` (`certain`/`uncertain`), `method`, `reviewer`, `reviewed_at` DATE, `note`.

### Databricks

Same tables, but geometry is stored as **BINARY WKB** without SRID (see `DATABRICKS.md`). Queries must use `ST_GeomFromWKB(geometry, 4326)`.

## 4. CRS

| Source | CRS | Axis order in data |
|---|---|---|
| OSM roads | EPSG:4326 | lon, lat |
| Overture segments | OGC:CRS84 | lon, lat |
| traffic_signs.geojson | EPSG:4326 (GeoJSON / WGS 84) | lon, lat |
| photos.csv | none (plain `longitude`, `latitude` columns) | lon, lat |
| Databricks | none (WKB); SRID must be given explicitly | lon, lat |

All inputs use geographic degrees. Distances must be computed after transforming to **EPSG:2180**. The EPSG:4326 definition declares lat/lon axis order, so transformations must force lon/lat order (e.g. `always_xy=True` in pyproj).

All 561 photo positions lie inside the bbox `19.80,49.95,20.15,50.15`. 560 OSM ways have `boundary_crossing = true`.

## 5. Geometry validity

| Source | Rows | Invalid | Type |
|---|---:|---:|---|
| OSM roads | 99,768 | 0 | LineString |
| Overture segments | 85,405 | 0 | LineString |
| traffic_signs | 1,730 | 0 | Point |

No repair step is needed at input. Validity is not checked in Databricks (the query is listed in `DATABRICKS.md`, but it was out of scope for the single read).

## 6. Duplicates

| Check | Result |
|---|---|
| `osm_roads.osm_id` | 99,768 unique, 0 duplicates |
| OSM identical geometries (WKB) | 0 |
| `overture_segments.id` | 85,405 unique, 0 duplicates |
| Overture identical geometries (WKB) | 0 |
| `photos.photo_id` / `sha256` / `source_sha256` | 561 / 561 / 561 unique |
| `photos` (longitude, latitude, captured_at) | **559 unique → 3 Panoramax photos share position and time** |
| `photo_road_links.photo_id` | 561 unique (exactly one row per photo) |
| `reference_labels` (photo_id, question) | 320 unique pairs, 0 duplicates |
| `traffic_signs.id` | 1,730 unique |

The 3 suspicious photos (`panoramax_5c501d68…`, `panoramax_0f839710…`, `panoramax_d34046cf…`) are at 19.96406, 50.0183, `2021-11-27 12:00:00+01`, with no heading. The image hashes differ, so they are different frames with **placeholder-looking metadata** (round time, identical coordinates). Position-based reasoning for them is unreliable.

## 7. Key relations (`photo_id` and road IDs)

| Relation | Orphans |
|---|---:|
| `photo_road_links.photo_id` → `photos` | 0 |
| `photos` → `photo_road_links` | 0 (1:1) |
| `reference_labels.photo_id` → `photos` | 0 |
| `photo_road_links.osm_way_id` → `osm_roads.osm_id` (non-null) | 0 |
| `photo_road_links.overture_id` → `overture_segments.id` (non-null) | 0 |
| `traffic_signs.image_ids` → `photos` (Mapillary `photo_id = 'mapillary_' + image id`) | 100 of 11,562 distinct image IDs are in `photos.csv`; all 100 Mapillary photos are referenced by a sign |

Other link facts:

- **Candidate coverage:** 558 photos have an OSM candidate and 558 an Overture candidate. 3 have `match_method = none` (`no_osm_within_25m`).
- **Match method:** 557 `osm_source_reference`, 1 `spatial_fallback`, 3 `none`.
- **Distance to candidate:** median 2.43 m, p95 9.82 m, max 22.17 m.
- **Photos per way:** 112 OSM ways have more than one photo; the busiest has 55. Photos are clustered, not independent samples of the network.
- **`candidate_flags`:** `ambiguous_candidates` 65, `camera_against_way_direction` 35, `panorama_heading_ambiguous` 31, `poor_heading_alignment` 27, `boundary_crossing` 27, `missing_heading` 15, `service_way` 14, `no_osm_within_25m` 3, `overture_spatial_only` 1.
- **`maxspeed` on photographed roads:** 544 photos link to non-`service`/`track` roads, and 531 of them (97.6%) have a numeric `maxspeed`. The 14 photos on `service`/`track` roads have none.
- **Overture provenance:** 84,614 / 85,405 segments (99.1%) list OpenStreetMap in `sources`. Overture is largely derived from OSM, so OSM–Overture agreement is weak independent evidence.

## 8. `maxspeed`: distribution and formats

### 8.1 OSM `maxspeed` column

| Format | Ways |
|---|---:|
| Missing (NULL) | 83,478 (83.7%) |
| Integer, km/h implied | 16,290 (16.3%) |
| Number with unit (`mph`, `km/h`) | 0 |
| `PL:urban` / other `CC:type` value | 0 |
| `none`, `signals`, `walk`, `variable` | 0 |
| Multiple values (`;`) | 0 |

Value distribution: 50 (5,737), 30 (4,802), 20 (2,053), 70 (1,294), 40 (1,245), 140 (214), 90 (184), 60 (181), 100 (167), 10 (157), 120 (134), 80 (61), 5 (48), 25 (7), 15 (4), 4 (2).

- **Low values:** 4–5 km/h appear on `service` (43), `living_street` (4) and `residential` (3). Plausible for car parks and private yards, but worth a plausibility rule.
- **Clean snapshot:** the `maxspeed` column itself has no units, no `none` and no multiple values. Text formats appear only in other keys (below). The parser must still handle them because `refresh_sources.py` can produce a newer snapshot.

### 8.2 Implicit and text values in other `maxspeed*` keys (inside `tags`)

| Key | Ways | Values |
|---|---:|---|
| `source:maxspeed` | 11,671 | `PL:urban` 4,371, `PL:zone30` 3,033, `sign` 2,090, `PL:living_street` 960, `PL:zone20` 303, `PL:zone40` 257, `PL:rural` 213, `PL:motorway` 209, `PL:expressway` 145, `PL:zone10` 42, `zone30` 26 (no country prefix), `PL:sign` 14, `PL:zone30;sign` 2 (**multiple values**), `survey` 1 |
| `maxspeed:type` | 2,578 | `PL:urban` 1,603, `PL:zone30` 564, `sign` 253, `PL:zone40` 59, `PL:rural` 55, `PL:zone20` 27, `PL:living_street` 12, `PL:zone` 5 |
| `maxspeed:source` (non-standard) | 23 | `PL:zone30`, `PL:urban`, `sign`, `pl:zone30` (**lowercase**) |
| `zone:maxspeed` | 19 | `PL:30` |
| `maxspeed:forward` / `:backward` | 261 / 247 | numeric (e.g. 40/50, 50/30); also `PL:urban` as a value (5 ways) |
| `maxspeed:conditional` | 92 | only `110 @ (Mo-Fr 06:00-18:00)` |
| `maxspeed:variable` | 82 | `yes` |
| `maxspeed:lanes` | 10 | `120\|120\|120\|80`, `120\|120\|120\|80\|80` (**per-lane values**) |
| `maxspeed:hgv` / `:bus` / `:trailer` | 1,007 / 1,031 / 1,028 | vehicle-specific (hgv: 80, 50, 70, 40) |

**Implicit limit without a numeric `maxspeed`** (1,475 ways): `PL:urban` 1,401, `PL:rural` 46, `sign` 19, `PL:expressway` 7, `PL:zone40` 2. These are not "missing data": the speed can be derived from Polish defaults (urban 50 km/h, rural 90 km/h), but `sign` without a number cannot.

**Implicit type vs numeric value (consistency):**

- **Consistent majority:** `PL:urban` + 50 (4,346), `PL:zone30` + 30 (3,512), `PL:living_street` + 20 (961).
- **Disagreeing combinations (QA candidates):** `PL:urban` + 70 (55), + 30 (24), + 40 (19), + 60 (5); `PL:zone30` + 50 (4), + 20 (5); `PL:living_street` + 30 (9); `PL:rural` + 50 (3), + 70 (15).
- **Conflicting keys:** 18 ways have both `source:maxspeed` and `maxspeed:type` with different values.
- **Mixed directional tagging:** 4 ways have `maxspeed` and `maxspeed:forward/backward` at the same time.

### 8.3 Overture `speed_limits`

- **Coverage:** 12,847 segments (15.0%) have at least one rule; 72,558 have none. Rules per segment: 1 (11,936), 2 (647), 3 (169), up to 13.
- **Units and fields:** all `max_speed.unit = km/h`; no `min_speed`; 16 rules have `is_max_speed_variable = true`.
- **Direction:** `when.heading` is `forward` in 218 rules and `backward` in 216.
- **Vehicle modes:** `when.mode` is `[bus, hgv]` in 401 rules, `[bus]` in 30 and `[hgv]` in 9. These rules must not be compared with the general car limit.
- **Time-conditional:** `when.during = Mo-Fr06:00-18:00` in 19 rules.
- **Partial segments:** many rules carry a `between` range. Such a limit applies to part of the segment only.

## 9. Missing data

| Field | Missing | Notes |
|---|---:|---|
| OSM `maxspeed` (numeric) | 83,478 / 99,768 | 74,410 of the gaps are `service` (70,116) + `track` (4,294) |
| OSM any speed information (numeric, implicit, directional) | 81,748 / 99,768 | 18,020 ways have some speed information |
| OSM `maxspeed`, main roads | motorway 6/459, trunk 4/147, primary 27/1,586, secondary 70/2,073 without any speed info | Main roads are nearly complete |
| OSM `maxspeed`, residential | 5,291 / 11,799 without any speed info | The main gap among public streets |
| OSM `surface` / `lanes` / `lit` | see the table in `profile_data.py` output | `lanes` and `lit` are sparse on minor roads |
| OSM `access` / `motor_vehicle` | `access=private` 13,975, `no` 875, `motor_vehicle=private` 826, `no` 106 | ~16k ways are not public for cars |
| Overture `speed_limits` | 72,558 / 85,405 | |
| Overture `class = unknown` | 844 | No OSM-equivalent class |
| `photos.heading` | 15 (Panoramax) | `heading = 0` in 23 photos is valid (north) and must not be read as missing |
| `photos.horizontal_accuracy_m` | 315 / 561 | Only 246 have it (values 4–5 m) |
| `photos` road candidate | 3 | `match_method = none` |
| Panoramas | 31 | `is_panorama` heuristic; heading ambiguous |
| `reference_labels` | 36 `uncertain` of 320 | Mapillary: 6/20 per question uncertain; speed labels only for 20 Mapillary photos (14 certain) |

**Time spread:**

- **Photos:** 2014-07-14 → 2026-10-18; 256 / 561 (45.6%) were taken before 2024 (Panoramax 203, Mapillary 53).
- **Traffic signs:** `first_seen_at` from 2014-05-02, `last_seen_at` up to 2026-10-28; 882 / 1,730 (51.0%) were last seen before 2024.
- **Map snapshots:** OSM 2026-11-01, Overture 2026-10-21.

## 10. Five facts that change the project

1. **"Missing `maxspeed`" is mostly not a map error.** 83.7% of ways lack a numeric value, but 74k of the gaps are `service`/`track` and 1,475 ways carry an implicit limit (`PL:urban` 1,401, `PL:rural` 46). The QA rule must work on an **effective speed** (numeric → implicit → unknown) and report by road class and access. Otherwise the report flags tens of thousands of irrelevant ways.
2. **Speed is not one number per way.** The parser must handle forward/backward (261/247), per-lane values (10), conditional time rules (92), variable signs (82), vehicle-specific limits (`hgv`/`bus`/`trailer`, ~1k each) and Overture rules with `between`, `heading` and `mode`. A flat `maxspeed` comparison yields false conflicts, especially with Overture `[bus, hgv]` rules (440).
3. **OSM vs Overture is not an independent check.** 99.1% of Overture segments cite OSM as a source. Disagreement mostly means a snapshot difference (2026-10-21 vs 2026-11-01), not proof of an error. The independent evidence is the photos and signs, so the design should treat them as primary for verdicts and Overture as context.
4. **Photo evidence is clustered, dated and partly unreliable.** 112 ways carry multiple photos (up to 55 on one way); 45.6% of photos and 51% of sign sightings predate 2024. In addition, 15 photos lack heading, 31 are panoramas, 3 have placeholder position/time and 3 have no road candidate. The pipeline needs explicit abstain statuses and per-way aggregation, plus age weighting or a date threshold.
5. **The local files and Databricks match in size, so the file path can be the system of record.** The counts are identical in all 5 tables, but Databricks stores WKB without SRID and lacks `reference_labels`. Local GeoParquet/CSV with DuckDB is sufficient and simpler for the pipeline; Databricks can serve as an optional cross-check rather than a runtime dependency.

## 11. Questions for the human

1. **Implicit limits:** should the QA report treat `PL:urban`/`PL:rural` without a number as **valid** (derived 50/90 km/h), or flag them as "should be explicit"? And should `PL:urban` + 70 (55 ways) be reported as a conflict or accepted as a signed exception?
2. **Scope by road class and access:** should `service`, `track` and ways with `access=private/no` be excluded from the `maxspeed` QA, reported separately, or included?
3. **Evidence age and the Databricks role:** what is the maximum age of a photo or sign sighting that may support a verdict (e.g. 2024+)? Is Databricks a required input of the pipeline, or only an optional cross-check of the local snapshot?
