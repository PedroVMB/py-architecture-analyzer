import streamlit as st
from analyzer.github_fetcher import download_repo_zip, unzip_to_folder
from analyzer.extractor import extract_uploaded_zip
from analyzer.metrics import analyze_project
from analyzer.scoring import compute_scores
from analyzer.report import generate_text_report, save_json_report
import os
import zipfile
import tempfile
import shutil

st.set_page_config(page_title="E-commerce Architecture Compare", layout="wide")

st.title("Comparador Arquitetural: DDD vs Não-DDD (E-commerce)")

with st.sidebar:
    st.header("Entrada")
    input_mode = st.radio("Como fornecer código?", ["GitHub URL", "Upload ZIP"])
    token = st.text_input("GitHub token (opcional, para repositórios privados/limite API)", type="password")
    if input_mode == "GitHub URL":
        repo_a = st.text_input("Repo 1 (URL ou owner/repo)")
        repo_b = st.text_input("Repo 2 (URL ou owner/repo)")
    else:
        up_a = st.file_uploader("Zip do projeto 1", type=['zip'])
        up_b = st.file_uploader("Zip do projeto 2", type=['zip'])
    st.write("---")
    st.header("Pesos (opcional)")
    w_man = st.slider("Peso - Manutenibilidade", 0.0, 1.0, 0.35)
    w_comp = st.slider("Peso - Complexidade", 0.0, 1.0, 0.25)
    w_cpl = st.slider("Peso - Acoplamento", 0.0, 1.0, 0.20)
    w_struct = st.slider("Peso - Estrutura/Domínio", 0.0, 1.0, 0.20)
    if abs((w_man + w_comp + w_cpl + w_struct) - 1.0) > 0.01:
        st.warning("Os pesos devem somar aproximadamente 1.0. Ajustarei automaticamente na execução.")

run = st.button("Rodar análise")

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
                # salva temporariamente
                tmpf = os.path.join(tmproot, f"proj{idx}.zip")
                with open(tmpf, 'wb') as fh:
                    fh.write(up.read())
                base = extract_uploaded_zip(tmpf)
            st.success(f"Projeto {idx} extraído em {base}")
            proj_paths.append(base)
            names.append(os.path.basename(base))
        # analisa cada
        st.info("Extraindo métricas...")
        metrics = []
        for p in proj_paths:
            m = analyze_project(p)
            metrics.append(m)
        # prepara pesos
        W = {'manutenibilidade': w_man, 'complexidade': w_comp, 'coupling': w_cpl, 'structure': w_struct}
        # normalize weights sum to 1
        s = sum(W.values())
        W = {k: (v/s) for k,v in W.items()}
        scores_a, scores_b = compute_scores(metrics[0], metrics[1], weights=W)
        # relatório
        report_text = generate_text_report(metrics[0], metrics[1], scores_a, scores_b, name_a=names[0], name_b=names[1])
        st.header("Relatório gerado")
        st.code(report_text, language='text')
        # tabela de métricas
        import pandas as pd
        df = pd.DataFrame([
            {
                'project': names[0],
                'loc': metrics[0]['loc'],
                'py_files': metrics[0]['num_py_files'],
                'avg_cc': metrics[0]['complexity']['avg_cc'],
                'avg_mi': metrics[0]['complexity']['avg_mi'],
                'coupling_links': metrics[0]['coupling']['total_import_links'],
                'domain_segments': metrics[0]['domain']['domain_segments'],
                'score': scores_a['final_score']
            },
            {
                'project': names[1],
                'loc': metrics[1]['loc'],
                'py_files': metrics[1]['num_py_files'],
                'avg_cc': metrics[1]['complexity']['avg_cc'],
                'avg_mi': metrics[1]['complexity']['avg_mi'],
                'coupling_links': metrics[1]['coupling']['total_import_links'],
                'domain_segments': metrics[1]['domain']['domain_segments'],
                'score': scores_b['final_score']
            }
        ])
        st.dataframe(df)
        # plot radar com plotly
        import plotly.express as px
        categories = ['manutenibilidade','complexidade','coupling','structure']
        radar_a = [scores_a['manutenibilidade'], scores_a['complexidade'], scores_a['coupling'], scores_a['structure']]
        radar_b = [scores_b['manutenibilidade'], scores_b['complexidade'], scores_b['coupling'], scores_b['structure']]
        radar_df = pd.DataFrame({
            'metric': categories + categories,
            'value': radar_a + radar_b,
            'project': [names[0]]*len(categories) + [names[1]]*len(categories)
        })
        fig = px.line_polar(radar_df, r='value', theta='metric', color='project', line_close=True)
        st.plotly_chart(fig, use_container_width=True)
        # salvar JSON
        out_json = os.path.join(tmproot, 'report.json')
        from analyzer.report import save_json_report
        payload = {
            'metrics': [metrics[0], metrics[1]],
            'scores': [scores_a, scores_b],
            'names': names
        }
        save_json_report(out_json, payload)
        st.success(f"Relatório JSON salvo em {out_json}")
    except Exception as e:
        st.error(f"Erro na execução: {e}")
    finally:
        st.info("Execução finalizada. Lembre de remover arquivos temporários se quiser.")
