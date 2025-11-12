"""
scoring.py — cálculo de pontuações ponderadas com base nas métricas coletadas
"""

DEFAULT_WEIGHTS = {
    'manutenibilidade': 0.35,
    'complexidade': 0.25,
    'coupling': 0.20,
    'structure': 0.20
}


def normalize(value, minv, maxv):
    """Normaliza valor em relação ao intervalo min/max (0–1)."""
    if maxv == minv:
        return 1.0
    v = (value - minv) / (maxv - minv)
    return max(0.0, min(1.0, v))


def compute_scores(metrics_a, metrics_b, weights=None):
    """
    Calcula scores ponderados para dois projetos.
    Retorna dicionários com pontuações 0–100 para cada métrica e score final.
    """
    w = weights or DEFAULT_WEIGHTS

    # Extrai métricas comparáveis
    vals = {
        'mi': [metrics_a['complexity']['avg_mi'], metrics_b['complexity']['avg_mi']],
        'cc': [metrics_a['complexity']['avg_cc'], metrics_b['complexity']['avg_cc']],
        'coupling': [metrics_a['coupling']['total_import_links'], metrics_b['coupling']['total_import_links']],
        'domains': [metrics_a['domain']['domain_segments'], metrics_b['domain']['domain_segments']]
    }

    # Define intervalos de normalização
    mi_min, mi_max = min(vals['mi']), max(vals['mi'])
    cc_min, cc_max = min(vals['cc']), max(vals['cc'])
    cpl_min, cpl_max = min(vals['coupling']), max(vals['coupling'])
    dom_min, dom_max = min(vals['domains']), max(vals['domains'])

    def score_for(m):
        """Aplica normalização e ponderação para um projeto."""
        mi = normalize(m['complexity']['avg_mi'], mi_min, mi_max)
        cc = 1.0 - normalize(m['complexity']['avg_cc'], cc_min, cc_max)  # menor é melhor
        cpl = 1.0 - normalize(m['coupling']['total_import_links'], cpl_min, cpl_max)
        dom = normalize(m['domain']['domain_segments'], dom_min, dom_max)

        # Subscores (0–100)
        sc_man = mi * 100
        sc_comp = cc * 100
        sc_cpl = cpl * 100
        sc_struct = dom * 100

        # Aplica pesos
        weighted_scores = {
            'manutenibilidade': sc_man * w['manutenibilidade'],
            'complexidade': sc_comp * w['complexidade'],
            'coupling': sc_cpl * w['coupling'],
            'structure': sc_struct * w['structure']
        }

        final = sum(weighted_scores.values())  # soma ponderada total
        return {
            **weighted_scores,
            'final_score': final
        }

    return score_for(metrics_a), score_for(metrics_b)
