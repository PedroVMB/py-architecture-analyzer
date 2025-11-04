import json
from analyzer.report import save_json_report

def test_save_json_report_creates_valid_file(tmp_path):
    path = tmp_path / "report.json"
    payload = {"test": True, "metrics": []}

    save_json_report(path, payload)

    assert path.exists()
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data["test"] is True
