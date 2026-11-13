from map_qa.core.enums import ComparisonStatus, Decision, LinkStatus
from map_qa.core.errors import (
    ConfigError, InputChanged, MapQaError, MissingCredential, SchemaMismatch, SourceUnavailable,
)


def test_exit_codes_per_adr_004():
    assert ConfigError("x").exit_code == 2
    assert SourceUnavailable("x").exit_code == 3
    assert MissingCredential("DATABRICKS_TOKEN").exit_code == 3
    assert SchemaMismatch("osm_roads", "maxspeed").exit_code == 4
    assert InputChanged("photos.csv").exit_code == 5
    assert issubclass(SchemaMismatch, MapQaError)


def test_missing_credential_names_variable_in_polish():
    msg = str(MissingCredential("DATABRICKS_TOKEN"))
    assert "DATABRICKS_TOKEN" in msg
    assert "Brak" in msg
    assert "\n" not in msg


def test_schema_mismatch_names_table_and_column():
    msg = str(SchemaMismatch("osm_roads", "maxspeed"))
    assert "osm_roads" in msg and "maxspeed" in msg


def test_status_sets():
    assert {s.value for s in ComparisonStatus} == {
        "agree", "disagree", "missing_osm", "missing_overture", "not_comparable", "ambiguous_link"}
    assert {s.value for s in LinkStatus} == {"ok", "ambiguous", "no_candidate"}
    assert {d.value for d in Decision} == {
        "answered", "answered_tier2", "abstain", "model_unavailable", "not_run_budget_or_error"}
