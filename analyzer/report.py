import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path


def show_report(metrics_a, metrics_b, scores_a, scores_b, name_a, name_b, weights):
    """
    Exibe relatório completo com seções:
    - Métricas brutas (não ponderadas)
    - Scores ponderados (dinâmicos)
    - Conclusão automática
    """

    st.title("📊 Relatório Comparativo de Métricas Arquiteturais")
    st.write(f"Comparação entre **{name_a}** e **{name_b}** em métricas reais e scores ponderados.")

    # === Seção 1: Métricas brutas (fixas) ===
    st.header("📏 Métricas Reais (não influenciadas por pesos)")
    df_summary = pd.DataFrame([
        {
            'Projeto': name_a,
            'LOC': metrics_a['loc'],
            'Arquivos Python': metrics_a['num_py_files'],
            'Complexidade Média (CC)': metrics_a['complexity']['avg_cc'],
            'Índice MI': metrics_a['complexity']['avg_mi'],
            'Acoplamento': metrics_a['coupling']['total_import_links'],
            'Domínios Detectados': metrics_a['domain']['domain_segments'],
            'Classes': metrics_a['ast']['classes'],
            'Funções': metrics_a['ast']['functions']
        },
        {
            'Projeto': name_b,
            'LOC': metrics_b['loc'],
            'Arquivos Python': metrics_b['num_py_files'],
            'Complexidade Média (CC)': metrics_b['complexity']['avg_cc'],
            'Índice MI': metrics_b['complexity']['avg_mi'],
            'Acoplamento': metrics_b['coupling']['total_import_links'],
            'Domínios Detectados': metrics_b['domain']['domain_segments'],
            'Classes': metrics_b['ast']['classes'],
            'Funções': metrics_b['ast']['functions']
        }
    ])

    # Mostra gráficos básicos (fixos)
    for col, title in [
        ('LOC', 'Linhas de Código'),
        ('Complexidade Média (CC)', 'Complexidade Ciclomática Média'),
        ('Índice MI', 'Índice de Manutenibilidade'),
        ('Acoplamento', 'Acoplamento Interno'),
        ('Domínios Detectados', 'Separação de Domínios')
    ]:
        fig = px.bar(df_summary, x='Projeto', y=col, color='Projeto', title=title)
        st.plotly_chart(fig, use_container_width=True)

    # === Seção 2: Scores ponderados (dinâmicos) ===
    st.header("⚖️ Scores Ponderados (influenciados pelos pesos)")

    df_weighted = pd.DataFrame({
        'Métrica': ['Manutenibilidade', 'Complexidade', 'Acoplamento', 'Estrutura/Domínio'],
        name_a: [scores_a['manutenibilidade'], scores_a['complexidade'],
                 scores_a['coupling'], scores_a['structure']],
        name_b: [scores_b['manutenibilidade'], scores_b['complexidade'],
                 scores_b['coupling'], scores_b['structure']]
    })

    df_weighted = df_weighted.melt(id_vars='Métrica', var_name='Projeto', value_name='Score Ponderado')
    fig_weighted = px.bar(df_weighted, x='Métrica', y='Score Ponderado', color='Projeto',
                          barmode='group', title='Impacto dos Pesos sobre as Métricas')
    st.plotly_chart(fig_weighted, use_container_width=True)

    # Radar ponderado
    st.subheader("📈 Radar de Comparação Ponderada")
    categories = ['manutenibilidade', 'complexidade', 'coupling', 'structure']
    radar_df = pd.DataFrame({
        'Métrica': categories + categories,
        'Valor Ponderado': [scores_a[m] for m in categories] + [scores_b[m] for m in categories],
        'Projeto': [name_a]*len(categories) + [name_b]*len(categories)
    })
    fig_radar = px.line_polar(radar_df, r='Valor Ponderado', theta='Métrica', color='Projeto', line_close=True)
    st.plotly_chart(fig_radar, use_container_width=True)

    # Score final
    st.subheader("🌐 Score Arquitetural Global")
    df_score = pd.DataFrame({
        'Projeto': [name_a, name_b],
        'Score Final (0–100)': [scores_a['final_score'], scores_b['final_score']]
    })
    fig_score = px.bar(df_score, x='Score Final (0–100)', y='Projeto', orientation='h',
                       color='Projeto', text='Score Final (0–100)')
    fig_score.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig_score, use_container_width=True)

    # === Conclusão automática ===
    st.header("🏁 Conclusão da Análise")
    if scores_a['final_score'] > scores_b['final_score']:
        diff = scores_a['final_score'] - scores_b['final_score']
        st.success(f"✅ **{name_a}** superou **{name_b}** por {diff:.1f} pontos. A arquitetura DDD apresentou melhor qualidade segundo os pesos atuais.")
    elif scores_b['final_score'] > scores_a['final_score']:
        diff = scores_b['final_score'] - scores_a['final_score']
        st.warning(f"⚠️ **{name_b}** superou **{name_a}** por {diff:.1f} pontos. A arquitetura tradicional apresentou melhor resultado segundo os pesos atuais.")
    else:
        st.info("⚖️ Ambos os projetos tiveram pontuações equivalentes.")

    st.markdown("""
    ---
    **Nota:** As métricas brutas refletem o estado real do código.  
    Os *scores ponderados* mudam conforme os pesos, permitindo simular prioridades diferentes
    (ex: priorizar manutenibilidade ou modularidade).
    """)

    with st.expander("📂 Debug e Pesos Aplicados"):
        st.json({"Pesos": weights})
        st.json({"Scores Projeto A": scores_a})
        st.json({"Scores Projeto B": scores_b})


def save_json_report(output_path, payload):
    """Salva o relatório como JSON no disco."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return str(p)
