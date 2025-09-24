import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path

def show_report(metrics_a, metrics_b, scores_a, scores_b, name_a, name_b):
    st.subheader("📊 Resumo Executivo")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Projeto 1", name_a)
        st.metric("Linhas de Código (LOC)", metrics_a['loc'])
        st.metric("Arquivos Python", metrics_a['num_py_files'])
        st.metric("Complexidade Média (CC)", f"{metrics_a['complexity']['avg_cc']:.2f}")
        st.metric("Índice de Manutenibilidade (MI)", f"{metrics_a['complexity']['avg_mi']:.2f}")
        st.metric("Acoplamento", metrics_a['coupling']['total_import_links'])
        st.metric("Domínios Detectados", metrics_a['domain']['domain_segments'])
        st.metric("Score Final", f"{scores_a['final_score']:.2f}")
    with col2:
        st.metric("Projeto 2", name_b)
        st.metric("Linhas de Código (LOC)", metrics_b['loc'])
        st.metric("Arquivos Python", metrics_b['num_py_files'])
        st.metric("Complexidade Média (CC)", f"{metrics_b['complexity']['avg_cc']:.2f}")
        st.metric("Índice de Manutenibilidade (MI)", f"{metrics_b['complexity']['avg_mi']:.2f}")
        st.metric("Acoplamento", metrics_b['coupling']['total_import_links'])
        st.metric("Domínios Detectados", metrics_b['domain']['domain_segments'])
        st.metric("Score Final", f"{scores_b['final_score']:.2f}")

    st.write("---")
    st.subheader("📑 Tabela Comparativa")
    df = pd.DataFrame([
        {
            'Projeto': name_a,
            'LOC': metrics_a['loc'],
            'Arquivos Python': metrics_a['num_py_files'],
            'Complexidade Média (CC)': metrics_a['complexity']['avg_cc'],
            'Índice MI': metrics_a['complexity']['avg_mi'],
            'Acoplamento': metrics_a['coupling']['total_import_links'],
            'Domínios Detectados': metrics_a['domain']['domain_segments'],
            'Score Final': scores_a['final_score']
        },
        {
            'Projeto': name_b,
            'LOC': metrics_b['loc'],
            'Arquivos Python': metrics_b['num_py_files'],
            'Complexidade Média (CC)': metrics_b['complexity']['avg_cc'],
            'Índice MI': metrics_b['complexity']['avg_mi'],
            'Acoplamento': metrics_b['coupling']['total_import_links'],
            'Domínios Detectados': metrics_b['domain']['domain_segments'],
            'Score Final': scores_b['final_score']
        }
    ])
    st.dataframe(df, use_container_width=True)

    st.write("---")
    st.subheader("📈 Comparação Visual por Métrica (Radar)")
    categories = ['manutenibilidade','complexidade','coupling','structure']
    radar_a = [scores_a['manutenibilidade'], scores_a['complexidade'], scores_a['coupling'], scores_a['structure']]
    radar_b = [scores_b['manutenibilidade'], scores_b['complexidade'], scores_b['coupling'], scores_b['structure']]
    radar_df = pd.DataFrame({
        'Métrica': categories + categories,
        'Valor': radar_a + radar_b,
        'Projeto': [name_a]*len(categories) + [name_b]*len(categories)
    })
    fig = px.line_polar(radar_df, r='Valor', theta='Métrica', color='Projeto', line_close=True)
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    st.subheader("📝 Análise Automática")
    if scores_a['final_score'] > scores_b['final_score']:
        st.success(f"✅ O projeto **{name_a}** apresentou melhor score geral, indicando maior qualidade arquitetural.")
    elif scores_b['final_score'] > scores_a['final_score']:
        st.success(f"✅ O projeto **{name_b}** apresentou melhor score geral, indicando maior qualidade arquitetural.")
    else:
        st.warning("⚖️ Ambos os projetos tiveram scores equivalentes — recomenda-se inspeção qualitativa.")

    st.info("ℹ️ Observação: métricas automáticas são apoio; recomenda-se avaliação qualitativa especialmente em **separação de domínio e coesão**.")


def save_json_report(output_path, payload):
    """Salva o relatório em formato JSON"""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return str(p)
