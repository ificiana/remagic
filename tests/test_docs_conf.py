from pathlib import Path
from runpy import run_path

CONF = Path(__file__).parent.parent / "docs" / "conf.py"


def test_docs_load_goatcounter() -> None:
    js_files = run_path(str(CONF))["html_js_files"]
    assert (
        "//gc.zgo.at/count.js",
        {
            "async": "async",
            "data-goatcounter": "https://ificiana-rm.goatcounter.com/count",
        },
    ) in js_files
