# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb==1.5.6", "geopandas==1.2.0", "osmium>=4.1,<5", "pyarrow==23.0.1"]
# ///
"""Pobiera i konwertuje źródła mapowe. Nie rozwiązuje dopasowań ani konfliktów."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent
BBOX = (19.80, 49.95, 20.15, 50.15)
DRIVABLE = {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "residential", "living_street", "unclassified", "service", "track", "road", "busway"}
COLUMNS = ["highway", "maxspeed", "surface", "lanes", "oneway", "lit", "sidewalk", "sidewalk:left", "sidewalk:right", "junction", "ref", "name", "access", "motor_vehicle", "bridge", "tunnel", "layer"]


def get_json(url: str) -> dict:
    with urlopen(Request(url, headers={"User-Agent": "JSystems-map-QA-course/2026"}), timeout=60) as response:
        return json.load(response)


def osm(args: argparse.Namespace) -> dict:
    import geopandas as gpd
    import osmium
    from shapely.geometry import LineString, box
    source = args.pbf or args.out / "malopolskie.osm.pbf"
    url = "https://download.geofabrik.de/europe/poland/malopolskie-latest.osm.pbf"
    if not source.exists():
        if shutil.disk_usage(args.out).free < 2 * 1024**3:
            raise RuntimeError("Potrzebne co najmniej 2 GB wolnego miejsca")
        temporary = source.with_suffix(".part")
        with urlopen(url, timeout=90) as response, temporary.open("xb") as target:
            shutil.copyfileobj(response, target, length=1024 * 1024)
        temporary.replace(source)
    with osmium.io.Reader(str(source)) as reader:
        extract_date = reader.header().get("osmosis_replication_timestamp")
    area = box(*args.bbox)

    class Handler(osmium.SimpleHandler):
        def __init__(self) -> None:
            super().__init__()
            self.rows: list[dict] = []

        def way(self, way) -> None:
            if way.tags.get("highway") not in DRIVABLE:
                return
            coordinates = [(node.lon, node.lat) for node in way.nodes]
            if len(coordinates) < 2:
                return
            line = LineString(coordinates)
            if not line.intersects(area):
                return
            tags = dict(way.tags)
            self.rows.append({"osm_id": way.id, "osm_version": way.version, "osm_timestamp": str(way.timestamp), "node_ids": [node.ref for node in way.nodes], "start_node": way.nodes[0].ref, "end_node": way.nodes[-1].ref, "boundary_crossing": not area.covers(line), "tags": json.dumps(tags, ensure_ascii=False, sort_keys=True), **{key: tags.get(key) for key in COLUMNS}, "geometry": line})

    handler = Handler()
    handler.apply_file(str(source), locations=True, idx="flex_mem")
    if not handler.rows:
        raise ValueError("Brak dróg OSM w wycinku")
    roads = gpd.GeoDataFrame(handler.rows, crs=4326)
    roads.to_parquet(args.out / "osm_roads.parquet", index=False, compression="zstd", compression_level=9)
    sample = roads.head(60).copy()
    sample["node_ids"] = sample.node_ids.map(list)
    sample.to_file(args.out / "osm_roads_sample.geojson", driver="GeoJSON")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    # Delete only the intermediate downloaded by this run, never a user-supplied PBF.
    if args.pbf is None:
        source.unlink()
    return {"url": url, "extract_date": extract_date, "pbf_sha256": source_hash, "rows": len(roads)}


def overture(args: argparse.Namespace) -> dict:
    import duckdb
    release = get_json("https://stac.overturemaps.org/catalog.json")["latest"]
    collection = get_json(f"https://stac.overturemaps.org/{release}/transportation/segment/collection.json")
    items = [link for link in collection["links"] if link["rel"] == "item"]
    extents = collection["extent"]["spatial"]["bbox"]
    if len(extents) != len(items) + 1:
        raise ValueError("Zmienił się układ katalogu STAC; sprawdź metadane przed pobraniem")
    west, south, east, north = args.bbox
    urls = []
    for link, bbox in zip(items, extents[1:]):
        if bbox[0] <= east and bbox[2] >= west and bbox[1] <= north and bbox[3] >= south:
            item = get_json(link["href"])
            if item["bbox"] != bbox:
                raise ValueError("Kolejność partycji STAC nie odpowiada zasięgom")
            urls.append(item["assets"]["aws"]["href"])
    if not urls:
        raise ValueError("Brak partycji Overture dla obszaru")
    connection = duckdb.connect()
    connection.execute("SET memory_limit='3GB'; SET threads=4; INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
    connection.execute("CREATE TABLE selected AS SELECT id,geometry,class,subclass,names.primary AS name,sources,connectors,speed_limits,road_surface,road_flags,access_restrictions,level_rules,bbox,version FROM read_parquet($urls) WHERE bbox.xmin <= $east AND bbox.xmax >= $west AND bbox.ymin <= $north AND bbox.ymax >= $south AND subtype='road' AND class NOT IN ('footway','path','steps','cycleway','pedestrian','bridleway')", {"urls": urls, "west": west, "south": south, "east": east, "north": north})
    connection.execute("COPY selected TO $target (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 9)", {"target": str(args.out / "overture_segments.parquet")})
    return {"release": release, "urls": urls, "rows": connection.execute("SELECT count(*) FROM selected").fetchone()[0]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=BASE / "data" / "refreshed")
    parser.add_argument("--pbf", type=Path, help="Istniejący pełny wyciąg małopolskiego; bez ponownego pobierania")
    parser.add_argument("--bbox", type=float, nargs=4, default=BBOX, metavar=("WEST", "SOUTH", "EAST", "NORTH"))
    parser.add_argument("--source", choices=["osm", "overture", "both"], default="both")
    args = parser.parse_args()
    west, south, east, north = args.bbox
    if not (18 < west < east < 22 and 48 < south < north < 52):
        parser.error("bbox musi być poprawnym wycinkiem okolic małopolskiego")
    args.out.mkdir(parents=True, exist_ok=True)
    expected = [name for source, name in [("osm", "osm_roads.parquet"), ("overture", "overture_segments.parquet")] if args.source in (source, "both")]
    if any((args.out / name).exists() for name in expected):
        parser.error("Katalog zawiera już wynik. Wybierz nowy --out")
    result = {"created_at": datetime.now(timezone.utc).isoformat(), "bbox": list(args.bbox)}
    for kind in ("osm", "overture"):
        if args.source in (kind, "both"):
            result[kind] = globals()[kind](args)
            (args.out / "refresh.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(kind, result[kind], flush=True)
    print("Nowe dane wymagają ponownego profilowania i dopasowania zdjęć w Twoim pipeline.")


if __name__ == "__main__":
    main()
