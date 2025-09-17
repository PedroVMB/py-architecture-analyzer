"""
Gera score ponderado a partir das métricas.
Pesos são configuráveis. O retorno é um dicionário com sub-scores e score final 0..100.
"""

DEFAULT_WEIGHTS = {
    'manutenibilidade': 0.35,   # usamos MI invertido (maior MI melhor)
    'complexidade': 0.25,       # menor complexity melhor
    'coupling': 0.20,           # menor coupling melhor
    'structure': 0.20           # domain segments e modularidade
}

def normalize(value, minv, maxv):
    if maxv == minv:
        return 1.0
    v = (value - minv) / (maxv - minv)
    return max(0.0, min(1.0, v))

def compute_scores(metrics_a, metrics_b, weights=None):
    w = weights or DEFAULT_WEIGHTS
    # Usamos comparações relativas entre os dois projetos para normalizar
    # Valores: metrics['complexity']['avg_cc'], metrics['complexity']['avg_mi'], coupling total, domain segments
    
    # gather raw
    vals = {
        'mi': [metrics_a['complexity']['avg_mi'], metrics_b['complexity']['avg_mi']],
        'cc': [metrics_a['complexity']['avg_cc'], metrics_b['complexity']['avg_cc']],
        'coupling': [metrics_a['coupling']['total_import_links'], metrics_b['coupling']['total_import_links']],
        'domains': [metrics_a['domain']['domain_segments'], metrics_b['domain']['domain_segments']]
    }
    # For MI (higher is better)
    mi_min, mi_max = min(vals['mi']), max(vals['mi'])
    cc_min, cc_max = min(vals['cc']), max(vals['cc'])
    cpl_min, cpl_max = min(vals['coupling']), max(vals['coupling'])
    dom_min, dom_max = min(vals['domains']), max(vals['domains'])
    def score_for(m):
        mi = normalize(m['complexity']['avg_mi'], mi_min, mi_max)
        cc = 1.0 - normalize(m['complexity']['avg_cc'], cc_min, cc_max) # lower is better
        cpl = 1.0 - normalize(m['coupling']['total_import_links'], cpl_min, cpl_max)
        dom = normalize(m['domain']['domain_segments'], dom_min, dom_max)
        # sub-scores
        sc_man = mi
        sc_comp = cc
        sc_cpl = cpl
        sc_struct = dom
        final = (w['manutenibilidade']*sc_man + w['complexidade']*sc_comp + w['coupling']*sc_cpl + w['structure']*sc_struct)
        # scale to 0..100
        return {
            'manutenibilidade': sc_man*100,
            'complexidade': sc_comp*100,
            'coupling': sc_cpl*100,
            'structure': sc_struct*100,
            'final_score': final*100
        }
    return score_for(metrics_a), score_for(metrics_b)
