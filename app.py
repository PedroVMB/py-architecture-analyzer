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

# Garante que nada fica cacheado de execução anterior
if "metrics" in st.session_state:
    del st.session_state["metrics"]
if "scores" in st.session_state:
    del st.session_state["scores"]

try:
    from analyzer.github_fetcher import download_repo_zip, unzip_to_folder
    from analyzer.extractor import extract_uploaded_zip
    from analyzer.metrics import analyze_project
    from analyzer.scoring import compute_scores
    
    # IMPORTANTE: Importa as funções do report.py
    from analyzer.report import show_report, save_json_report 
except ImportError as e:
    st.error(f"Erro de importação: {e}")
    st.error("Verifique se todos os arquivos (github_fetcher.py, extractor.py, metrics.py, scoring.py, report.py) existem dentro da pasta 'analyzer' e se a pasta 'analyzer' contém um arquivo __init__.py.")
    st.stop()


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
        repo_a = st.text_input("Projeto 1: Repositório DDD (URL)")
        repo_b = st.text_input("Projeto 2: Arq. Tradicional (URL)")
    else:
        up_a = st.file_uploader("Projeto 1: Repositório DDD (ZIP)", type=['zip'])
        up_b = st.file_uploader("Projeto 2: Arq. Tradicional (ZIP)", type=['zip'])

    st.write("---")
    st.header("⚖️ Pesos (opcional)")
    w_man = st.slider("Peso - Manutenibilidade", 0.0, 1.0, 0.35)
    w_comp = st.slider("Peso - Complexidade", 0.0, 1.0, 0.25)
    w_cpl = st.slider("Peso - Acoplamento", 0.0, 1.0, 0.20)
    w_struct = st.slider("Peso - Estrutura/Domínio", 0.0, 1.0, 0.20)
    if abs((w_man + w_comp + w_cpl + w_struct) - 1.0) > 0.01:
        st.warning("Os pesos devem somar aproximadamente 1.0. Ajustarei automaticamente na execução.")

st.caption(f"Pesos atuais: Manutenibilidade {w_man:.2f} | Complexidade {w_comp:.2f} | Acoplamento {w_cpl:.2f} | Estrutura {w_struct:.2f}")

if st.button("▶️ Rodar análise"):
    st.session_state["force_run"] = datetime.now().timestamp()


# ----------------------------
# Execução principal
# ----------------------------
if "force_run" in st.session_state:

    tmproot = tempfile.mkdtemp()
    proj_paths = []
    
    # Define os nomes explicitamente para usar no relatório
    names = ["Projeto DDD", "Projeto Tradicional"]
    
    try:
        for idx in [1,2]:
            # Usa o nome correto no log
            st.info(f"Processando Projeto {idx} ({names[idx-1]})...")
            
            if input_mode == "GitHub URL":
                url = repo_a if idx==1 else repo_b
                if not url:
                    st.error("Informe as duas URLs antes de rodar.")
                    st.stop() # Use st.stop() para parar a execução
                
                zip_path = download_repo_zip(url, dest_folder=tmproot, token=token if token else None)
                base = unzip_to_folder(zip_path, None)
            else:
                up = up_a if idx==1 else up_b
                if up is None:
                    st.error("Faça upload dos dois zips antes de rodar.")
                    st.stop() # Use st.stop() para parar a execução
                
                tmpf = os.path.join(tmproot, f"proj{idx}.zip")
                with open(tmpf, 'wb') as fh:
                    fh.write(up.read())
                
                base = extract_uploaded_zip(tmpf)

            st.success(f"Projeto {idx} extraído em {base}")
            proj_paths.append(base)

        st.info("Extraindo métricas...")
        metrics = [analyze_project(p) for p in proj_paths]

        W = {'manutenibilidade': w_man, 'complexidade': w_comp, 'coupling': w_cpl, 'structure': w_struct}
        s = sum(W.values())
        if s == 0:
            st.warning("Soma dos pesos é 0. Usando pesos padrão.")
            s = 1.0 # Evita divisão por zero se todos os sliders forem 0
        W = {k: (v/s) for k,v in W.items()}  # normaliza pesos

        scores_a, scores_b = compute_scores(metrics[0], metrics[1], weights=W)

        # --- MUDANÇA AQUI ---
        # Passa os nomes "Projeto DDD", "Projeto Tradicional" e os PESOS (W) para o relatório
        show_report(metrics[0], metrics[1], scores_a, scores_b, names[0], names[1], W)
        # --- FIM DA MUDANÇA ---

        # Salvar JSON
        out_json = os.path.join(tmproot, 'report.json')
        
        # Salva os nomes corretos no JSON também
        payload = {'metrics': [metrics[0], metrics[1]], 'scores': [scores_a, scores_b], 'names': names, 'weights': W}
        
        # Chama a função importada de report.py
        save_json_report(out_json, payload)
        
        st.success(f"📂 Relatório JSON salvo em {out_json}")

    except Exception as e:
        st.error(f"❌ Erro na execução: {e}")
        st.exception(e) # st.exception(e) é melhor para debug
    finally:
        st.info("✅ Execução finalizada.")