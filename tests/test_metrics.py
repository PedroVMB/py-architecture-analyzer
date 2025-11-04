import os
from analyzer.metrics import analyze_project

def test_analyze_project_returns_expected_keys(tmp_path):
    # cria projeto fictício
    sample_file = tmp_path / "sample.py"
    sample_file.write_text("def soma(a, b):\n    return a + b\n")

    result = analyze_project(tmp_path)

    assert 'loc' in result
    assert 'num_py_files' in result
    assert 'complexity' in result
    assert 'coupling' in result
    assert 'domain' in result
    assert isinstance(result['loc'], int)
    assert result['num_py_files'] == 1
