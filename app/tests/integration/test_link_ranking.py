"""ADR-002 §3.2 characterization test of the input ranking rule (sources.json `links`):
rank = distance_m + bearing_diff/9 (missing heading: +5 m), ties by distance then osm_id, radius 25 m.

On 10 random (seed 42) photos that have alternatives, the candidate chosen in photo_road_links.csv must have the
minimal rank among OSM ways within 25 m. A mismatch does not change the pipeline; it is a data finding
(the test prints it). Bearings: local tangent within +/-5 m of the projected camera, in EPSG:2180, converted to
true north with the PUWG 1992 meridian convergence (gamma ~ (lon - 19) * sin(lat)).
"""
import math
import random

from shapely import wkt

from map_qa.matching.pairs import link_rank, undirected_diff
from map_qa.sources import connect
from map_qa.sources.files import FilesSource

TOL_RANK_M = 0.5  # tangent/convergence approximation vs the source implementation


def test_chosen_candidate_has_minimal_rank(data_dir):
    con = connect(data_dir / "data")
    FilesSource(data_dir).load(con)
    rows = con.execute("""SELECT l.photo_id, l.osm_way_id, l.distance_m, p.heading, p.longitude, p.latitude
                          FROM photo_road_links l JOIN photos p USING (photo_id)
                          WHERE l.osm_way_id IS NOT NULL AND l.osm_candidate_count > 1 ORDER BY l.photo_id""").fetchall()
    sample = random.Random(42).sample(rows, 10)
    findings, checked = [], 0
    for pid, chosen, dist_file, heading, lon, lat in sample:
        cands = con.execute("""
            WITH cam AS (SELECT ST_Transform(ST_Point(?, ?), 'EPSG:4326', 'EPSG:2180', always_xy := true) AS camera_2180)
            SELECT o.osm_id, ST_AsText(ST_Transform(o.geometry, 'EPSG:4326', 'EPSG:2180', always_xy := true)) AS road,
                   ST_AsText(cam.camera_2180) AS cam
            FROM osm_roads o, cam
            WHERE ST_DWithin(ST_Transform(o.geometry, 'EPSG:4326', 'EPSG:2180', always_xy := true), cam.camera_2180, 25)
            """, [lon, lat]).fetchall()
        scored = []
        gamma = (lon - 19.0) * math.sin(math.radians(lat))
        for osm_id, road_wkt, cam_wkt in cands:
            line, cam = wkt.loads(road_wkt), wkt.loads(cam_wkt)
            s = line.project(cam)
            a, b = line.interpolate(max(0.0, s - 5)), line.interpolate(min(line.length, s + 5))
            grid = math.degrees(math.atan2(b.x - a.x, b.y - a.y)) % 360
            bd = undirected_diff(heading, (grid + gamma) % 360)
            d = line.distance(cam)
            scored.append((link_rank(d, bd), d, osm_id))
        assert any(c[2] == chosen for c in scored), pid
        best = min(scored)
        mine = next(c for c in scored if c[2] == chosen)
        assert abs(mine[1] - dist_file) < 0.5, pid  # same metric distance as the input
        checked += 1
        if mine[0] - best[0] > TOL_RANK_M:
            findings.append((pid, chosen, round(mine[0], 2), best[2], round(best[0], 2)))
    print(f"ranking characterization: {checked} photos checked, findings: {findings}")
    con.close()
    assert checked == 10
    assert not findings, f"input ranking differs from sources.json rule (data finding): {findings}"
