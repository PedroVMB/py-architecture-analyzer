import os
import zipfile
import tempfile
import shutil
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import streamlit as st
import pandas as pd
import plotly.express as px

from analyzer.github_fetcher import download_repo_zip, unzip_to_folder
from analyzer.extractor import extract_uploaded_zip
from analyzer.metrics import analyze_project
from analyzer.scoring import compute_scores
from analyzer.report import save_json_report

# ----------------------------
# Configuração inicial
# ----------------------------
st.set_page_config(page_title="E-commerce Architecture Compare", layout="wide")

st.title("⚖️ Comparador Arquitetural: DDD vs Não-DDD (E-commerce)")

# ----------------------------
# Sidebar de entrada
# ----------------------------
with st.sidebar:
    st.header("📥 Entrada")
    input_mode = st.radio("Como fornecer código?", ["GitHub URL", "Upload ZIP"])
    token = st.text_input("GitHub token (opcional, para repositórios privados/limite API)", type="password")
    if input_mode == "GitHub URL":
        repo_a = st.text_input("Repo 1 (URL ou owner/repo)")
        repo_b = st.text_input("Repo 2 (URL ou owner/repo)")
    else:
        up_a = st.file_uploader("Zip do projeto 1", type=['zip'])
        up_b = st.file_uploader("Zip do projeto 2", type=['zip'])

    st.write("---")
    st.header("⚖️ Pesos (opcional)")
    w_man = st.slider("Peso - Manutenibilidade", 0.0, 1.0, 0.35)
    w_comp = st.slider("Peso - Complexidade", 0.0, 1.0, 0.25)
    w_cpl = st.slider("Peso - Acoplamento", 0.0, 1.0, 0.20)
    w_struct = st.slider("Peso - Estrutura/Domínio", 0.0, 1.0, 0.20)
    if abs((w_man + w_comp + w_cpl + w_struct) - 1.0) > 0.01:
        st.warning("Os pesos devem somar aproximadamente 1.0. Ajustarei automaticamente na execução.")

run = st.button("▶️ Rodar análise")

# ----------------------------
# Função de exibição do relatório
# ----------------------------
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

    # Comparação em tabela
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

    # Radar chart
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

    # Conclusão automática
    st.subheader("📝 Análise Automática")
    if scores_a['final_score'] > scores_b['final_score']:
        st.success(f"✅ O projeto **{name_a}** apresentou melhor score geral, indicando maior qualidade arquitetural.")
    elif scores_b['final_score'] > scores_a['final_score']:
        st.success(f"✅ O projeto **{name_b}** apresentou melhor score geral, indicando maior qualidade arquitetural.")
    else:
        st.warning("⚖️ Ambos os projetos tiveram scores equivalentes — recomenda-se inspeção qualitativa.")

    st.info("ℹ️ Observação: métricas automáticas são apoio; recomenda-se avaliação qualitativa especialmente em **separação de domínio e coesão**.")

# ----------------------------
# Execução principal
# ----------------------------
if run:
    tmproot = tempfile.mkdtemp()
    proj_paths = []
    names = []
    try:
        for idx in [1,2]:
            st.info(f"Processando projeto {idx}...")
            if input_mode == "GitHub URL":
                url = repo_a if idx==1 else repo_b
                if not url:
                    st.error("Informe as duas URLs antes de rodar.")
                    raise SystemExit()
                zip_path = download_repo_zip(url, dest_folder=tmproot, token=token if token else None)
                base = unzip_to_folder(zip_path, None)
            else:
                up = up_a if idx==1 else up_b
                if up is None:
                    st.error("Faça upload dos dois zips antes de rodar.")
                    raise SystemExit()
                tmpf = os.path.join(tmproot, f"proj{idx}.zip")
                with open(tmpf, 'wb') as fh:
                    fh.write(up.read())
                base = extract_uploaded_zip(tmpf)

            st.success(f"Projeto {idx} extraído em {base}")
            proj_paths.append(base)
            names.append(os.path.basename(base))

        st.info("Extraindo métricas...")
        metrics = [analyze_project(p) for p in proj_paths]

        W = {'manutenibilidade': w_man, 'complexidade': w_comp, 'coupling': w_cpl, 'structure': w_struct}
        s = sum(W.values())
        W = {k: (v/s) for k,v in W.items()}  # normaliza pesos

        scores_a, scores_b = compute_scores(metrics[0], metrics[1], weights=W)

        # Exibir relatório novo
        show_report(metrics[0], metrics[1], scores_a, scores_b, names[0], names[1])

        # Salvar JSON
        out_json = os.path.join(tmproot, 'report.json')
        payload = {'metrics': [metrics[0], metrics[1]], 'scores': [scores_a, scores_b], 'names': names}
        save_json_report(out_json, payload)
        st.success(f"📂 Relatório JSON salvo em {out_json}")

    except Exception as e:
        st.error(f"❌ Erro na execução: {e}")
    finally:
        st.info("✅ Execução finalizada. Lembre de remover arquivos temporários se quiser.")
