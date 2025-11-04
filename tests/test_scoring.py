from analyzer.scoring import compute_scores

def test_compute_scores_output_structure():
    metrics_a = {
        'complexity': {'avg_mi': 80, 'avg_cc': 1.5},
        'coupling': {'total_import_links': 5},
        'domain': {'domain_segments': 4},
        'loc': 5000
    }
    metrics_b = {
        'complexity': {'avg_mi': 90, 'avg_cc': 2.0},
        'coupling': {'total_import_links': 8},
        'domain': {'domain_segments': 2},
        'loc': 5500
    }

    weights = {'manutenibilidade': 0.35, 'complexidade': 0.25, 'coupling': 0.2, 'structure': 0.2}
    scores_a, scores_b = compute_scores(metrics_a, metrics_b, weights)

    assert 'final_score' in scores_a
    assert 'final_score' in scores_b
    assert 0 <= scores_a['final_score'] <= 100
    assert 0 <= scores_b['final_score'] <= 100
