"""ADR-001 §3.4 `lit` (OSM only; compared with photo reading, never with Overture)."""
import pytest

from map_qa.normalize.lit import lit_class


@pytest.mark.parametrize("raw,cls", [("yes", "yes"), ("no", "no"), ("automatic", "yes_conditional"),
                                     ("24/7", "yes_conditional"), ("sunset-sunrise", "yes_conditional"),
                                     (None, "missing"), ("", "missing"), ("YES", "yes"),
                                     ("disused", "unknown_value")])
def test_lit_classes(raw, cls):
    assert lit_class(raw) == cls
