# Map QA input data profile

- **Date:** 2026-11-12
- **Command:** `uv run --python 3.12 course-materials/exercise-data/map-qa/profile_data.py` (run with `PYTHONUTF8=1` on Windows; without it the console encoding cp1250 crashes `result.show()`)
- **Engine:** DuckDB + spatial extension, local files in `course-materials/exercise-data/map-qa/`
- **Scope:** local files only. No Databricks, no external APIs, input data unchanged.

## Row counts

| Source | File | Rows | Unique IDs |
|---|---|---:|---:|
| OSM roads | `osm_roads.parquet` | 99,768 | 99,768 (`osm_id`) |
| Overture segments | `overture_segments.parquet` | 85,405 | 85,405 (`id`) |
| Photos | `photos.csv` | 561 | – |
| Photo-road links | `photo_road_links.csv` | 561 | – |

`traffic_signs.geojson` (1,730 rows according to `DATABRICKS.md`) is not covered by the profiling script.

Different segmentation and filters mean the OSM and Overture counts do not measure agreement between the sources.

## CRS and geometry validity

| Source | Geometry type | CRS | Invalid geometries |
|---|---|---|---:|
| OSM roads | `GEOMETRY('EPSG:4326')` | EPSG:4326 | 0 |
| Overture segments | `GEOMETRY('OGC:CRS84')` | OGC:CRS84 | 0 |

Both files store coordinates as longitude/latitude. Distances must be computed after transforming to **EPSG:2180** (metres). The CRS labels differ (EPSG:4326 vs OGC:CRS84), so an explicit, consistent axis order is needed when combining the sources.

## OSM: attribute completeness by `highway`

| highway | rows | maxspeed | surface | lanes | lit |
|---|---:|---:|---:|---:|---:|
| service | 72,113 | 1,997 | 17,390 | 849 | 3,379 |
| residential | 11,799 | 5,467 | 9,598 | 2,334 | 5,103 |
| track | 4,296 | 2 | 1,657 | 0 | 86 |
| tertiary | 3,838 | 2,839 | 3,772 | 2,888 | 2,451 |
| secondary | 2,073 | 1,897 | 2,065 | 2,015 | 1,633 |
| living_street | 1,938 | 1,140 | 1,524 | 109 | 638 |
| primary | 1,586 | 1,539 | 1,584 | 1,562 | 1,260 |
| unclassified | 880 | 316 | 770 | 342 | 331 |
| motorway | 459 | 453 | 453 | 454 | 213 |
| motorway_link | 229 | 192 | 226 | 214 | 116 |
| secondary_link | 180 | 142 | 178 | 166 | 166 |
| trunk | 147 | 143 | 129 | 143 | 45 |
| primary_link | 127 | 110 | 127 | 119 | 116 |
| trunk_link | 54 | 21 | 44 | 42 | 9 |
| tertiary_link | 46 | 32 | 46 | 36 | 42 |
| road | 2 | 0 | 2 | 0 | 1 |
| busway | 1 | 0 | 1 | 0 | 0 |

### Missing `maxspeed`

- All ways: **16,290 / 99,768 (16.3%)** have `maxspeed`; **83,478 (83.7%)** are missing it.
- Excluding `service` and `track`: **14,291 / 23,359 (61.2%)** have `maxspeed`.
- Main roads (`motorway`, `trunk`, `primary`, `secondary`) are 92–99% complete; `service` is 2.8% complete and `track` is almost empty.
- Directional and conditional variants appear in `tags`: `maxspeed:forward` 261, `maxspeed:backward` 247, `maxspeed:conditional` 92. A plain `maxspeed` check is not enough for these ways.
- `boundary_crossing = true`: 560 ways cross the study area boundary.

## Overture: attribute completeness by `class`

| class | rows | with speed_limits | with road_surface |
|---|---:|---:|---:|
| service | 60,968 | 1,624 | 14,027 |
| residential | 11,185 | 5,129 | 8,781 |
| track | 3,663 | 2 | 1,321 |
| tertiary | 3,102 | 2,180 | 3,032 |
| living_street | 2,278 | 1,378 | 1,768 |
| secondary | 1,335 | 1,192 | 1,303 |
| primary | 916 | 840 | 896 |
| unknown | 844 | 2 | 8 |
| unclassified | 816 | 262 | 704 |
| motorway | 211 | 172 | 187 |
| trunk | 87 | 66 | 81 |

- Segments with speed rules: **12,847 / 85,405 (15.0%)**.
- `speed_limits` and `road_surface` are nested lists of rules that are not flattened. Comparing them with OSM requires interpreting the rules (between, direction, when).
- Overture has no separate `*_link` classes and has 844 `unknown` segments, so the class mapping between OSM and Overture is not 1:1.

## Photos (`photos.csv`)

| source | rows | sequences | with heading | with author | with license |
|---|---:|---:|---:|---:|---:|
| Panoramax | 461 | 56 | 446 | 461 | 461 |
| Mapillary | 100 | 52 | 100 | 100 | 100 |

- 15 Panoramax photos have no `heading`, so a heading-based match cannot be checked for them.
- Author and license are complete, so attribution is possible for every photo.

## Photo-road links (`photo_road_links.csv`)

| metric | value |
|---|---:|
| photos | 561 |
| with OSM candidate | 558 |
| with Overture candidate | 558 |
| min distance | 0.0 m |
| median distance | 2.43 m |
| p95 distance | 9.82 m |
| max distance | 22.17 m |

| match_method | rows |
|---|---:|
| osm_source_reference | 557 |
| spatial_fallback | 1 |
| none | 3 |

- 3 photos have no candidate (`none`), and the pipeline must handle them explicitly rather than drop them.
- All distances are within the 25 m candidate radius described in `sources.json`.

## Implications for ADRs and the plan

1. Compute metric distances in EPSG:2180, never in degrees.
2. Most missing `maxspeed` comes from `service`/`track` roads. The QA report should segment results by road class, otherwise those classes dominate the statistics.
3. Speed comparison must account for directional/conditional OSM tags and nested Overture rules.
4. Photos without heading (15) or without a road candidate (3) need explicit statuses in the output.
5. Geometry is valid in both sources, so no repair step is needed at input.

## Not yet verified

- Databricks table counts versus local files (planned cross-check; expected the same counts).
- `traffic_signs.geojson` and `signs/` set: not profiled here.
