import json
from datetime import datetime
from pathlib import Path

def generate_text_report(metrics_a, metrics_b, scores_a, scores_b, name_a='Project A', name_b='Project B'):
    now = datetime.utcnow().isoformat()
    lines = []
    lines.append(f"Relatório de comparação arquitetural - {now}")
    lines.append("")
    lines.append("RESUMO EXECUTIVO")
    lines.append(f"- Projeto 1: {name_a}")
    lines.append(f"- Projeto 2: {name_b}")
    lines.append("")
    lines.append("MÉTRICAS PRINCIPAIS")
    lines.append(f"{name_a} - LOC: {metrics_a['loc']}, arquivos python: {metrics_a['num_py_files']}, avg CC: {metrics_a['complexity']['avg_cc']:.2f}, avg MI: {metrics_a['complexity']['avg_mi']:.2f}, coupling: {metrics_a['coupling']['total_import_links']}")
    lines.append(f"{name_b} - LOC: {metrics_b['loc']}, arquivos python: {metrics_b['num_py_files']}, avg CC: {metrics_b['complexity']['avg_cc']:.2f}, avg MI: {metrics_b['complexity']['avg_mi']:.2f}, coupling: {metrics_b['coupling']['total_import_links']}")
    lines.append("")
    lines.append("SCORES (0..100)")
    lines.append(f"{name_a} final score: {scores_a['final_score']:.2f}")
    lines.append(f"{name_b} final score: {scores_b['final_score']:.2f}")
    lines.append("")
    lines.append("ANÁLISE")
    if scores_a['final_score'] > scores_b['final_score']:
        lines.append(f"O projeto {name_a} apresenta melhor score geral (mais manutenível/menos complexo etc.).")
    elif scores_a['final_score'] < scores_b['final_score']:
        lines.append(f"O projeto {name_b} apresenta melhor score geral.")
    else:
        lines.append("Scores idênticos - análise qualitativa recomendada.")
    lines.append("")
    lines.append("OBSERVAÇÕES")
    lines.append("- Repare que DDD tende a aumentar LOC e número de módulos (mais verboso) mas melhora MI e reduz acoplamento.")
    lines.append("- Métricas automáticas são apoio; recomenda-se inspeção qualitativa especialmente em domain separation e coesão.")
    return "\n".join(lines)

def save_json_report(output_path, payload):
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return str(p)
