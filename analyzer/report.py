import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path

# --- MUDANÇA AQUI ---
# A função agora aceita 'weights' (pesos) vindos do app.py
def show_report(metrics_a, metrics_b, scores_a, scores_b, name_a, name_b, weights):
# --- FIM DA MUDANÇA ---

    st.title("📊 Relatório Comparativo de Métricas Arquiteturais")
    st.write(f"Análise visual e quantitativa entre **{name_a}** e **{name_b}**.") # Título atualizado

    # Tenta acessar as chaves com segurança
    try:
        # === Dados base ===
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
                'Funções': metrics_a['ast']['functions'],
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
                'Classes': metrics_b['ast']['classes'],
                'Funções': metrics_b['ast']['functions'],
                'Score Final': scores_b['final_score']
            }
        ])
        
        # Pega os valores para facilitar a comparação
        # val_a é "Projeto DDD", val_b é "Projeto Tradicional"
        val_a = df_summary.iloc[0]
        val_b = df_summary.iloc[1]

    except KeyError as e:
        st.error(f"❌ Erro ao processar os dados: a chave {e} está faltando nas métricas.")
        st.write("Verifique a saída da função `analyze_project`.")
        return

    # === Gráficos por métrica ===
    st.subheader("📏 Linhas de Código (LOC)")
    fig_loc = px.bar(df_summary, x='LOC', y='Projeto', orientation='h', color='Projeto',
                     title='Comparativo de Linhas de Código (LOC)')
    st.plotly_chart(fig_loc, use_container_width=True)
    st.markdown(f"💡 **Observação:** O **{name_a}** possui **{val_a['LOC']}** linhas de código, enquanto **{name_b}** possui **{val_b['LOC']}**.")
    st.markdown("*(LOC é uma métrica de tamanho; 'melhor' depende do contexto. Projetos DDD podem ser maiores devido à separação explícita de camadas.)*")


    st.subheader("⚙️ Complexidade Ciclomática Média (CC)")
    fig_cc = px.bar(df_summary, x='Projeto', y='Complexidade Média (CC)', color='Projeto',
                    title='Complexidade Ciclomática Média por Projeto')
    st.plotly_chart(fig_cc, use_container_width=True)
    if val_a['Complexidade Média (CC)'] < val_b['Complexidade Média (CC)']:
        st.info(f"💡 **Análise (Complexidade):** O **{name_a}** vence, com **menor** complexidade média ({val_a['Complexidade Média (CC)']:.2f}) que {name_b} ({val_b['Complexidade Média (CC)']:.2f}). Menor complexidade é geralmente melhor.")
    else:
        st.info(f"💡 **Análise (Complexidade):** O **{name_b}** vence, com **menor** complexidade média ({val_b['Complexidade Média (CC)']:.2f}) que {name_a} ({val_a['Complexidade Média (CC)']:.2f}). Menor complexidade é geralmente melhor.")

    st.subheader("🧠 Índice de Manutenibilidade (MI)")
    fig_mi = px.bar(df_summary, x='Projeto', y='Índice MI', color='Projeto',
                    title='Índice de Manutenibilidade (MI)')
    st.plotly_chart(fig_mi, use_container_width=True)
    if val_a['Índice MI'] > val_b['Índice MI']:
        st.info(f"💡 **Análise (Manutenibilidade):** O **{name_a}** vence, com **maior** índice ({val_a['Índice MI']:.2f}) que {name_b} ({val_b['Índice MI']:.2f}). Scores mais altos indicam código mais fácil de manter.")
    else:
        st.info(f"💡 **Análise (Manutenibilidade):** O **{name_b}** vence, com **maior** índice ({val_b['Índice MI']:.2f}) que {name_a} ({val_a['Índice MI']:.2f}). Scores mais altos indicam código mais fácil de manter.")


    st.subheader("🔗 Acoplamento entre Módulos")
    fig_cpl = px.bar(df_summary, x='Projeto', y='Acoplamento', color='Projeto',
                     title='Nível de Acoplamento entre Componentes Internos')
    st.plotly_chart(fig_cpl, use_container_width=True)
    if val_a['Acoplamento'] < val_b['Acoplamento']:
        st.info(f"💡 **Análise (Acoplamento):** O **{name_a}** vence, com **menor** acoplamento ({val_a['Acoplamento']}) que {name_b} ({val_b['Acoplamento']}). Menor acoplamento (menos importações internas) é crucial para a independência dos módulos.")
    else:
        st.info(f"💡 **Análise (Acoplamento):** O **{name_b}** vence, com **menor** acoplamento ({val_b['Acoplamento']}) que {name_a} ({val_a['Acoplamento']}). Menor acoplamento (menos importações internas) é crucial para a independência dos módulos.")


    st.subheader("🏗️ Estrutura de Domínio Detectada")
    fig_dom = px.pie(df_summary, values='Domínios Detectados', names='Projeto',
                     title='Distribuição de Domínios Detectados')
    st.plotly_chart(fig_dom, use_container_width=True)
    if val_a['Domínios Detectados'] > val_b['Domínios Detectados']:
        st.info(f"💡 **Análise (Domínio):** O **{name_a}** parece ter **melhor separação** de domínio ({val_a['Domínios Detectados']} segmentos) que {name_b} ({val_b['Domínios Detectados']}). Isso é um forte indicador de uma abordagem DDD.")
    else:
        st.info(f"💡 **Análise (Domínio):** O **{name_b}** parece ter **melhor separação** de domínio ({val_b['Domínios Detectados']} segmentos) que {name_a} ({val_a['Domínios Detectados']}).")


    st.subheader("🧩 Classes e Funções")
    df_long = df_summary.melt(id_vars='Projeto', value_vars=['Classes', 'Funções'],
                              var_name='Tipo', value_name='Quantidade')
    fig_ast = px.bar(df_long, x='Projeto', y='Quantidade', color='Tipo',
                     barmode='group', title='Distribuição de Classes e Funções')
    st.plotly_chart(fig_ast, use_container_width=True)
    st.markdown(f"💡 **Observação:** **{name_a}** possui **{val_a['Classes']}** classes e **{val_a['Funções']}** funções. **{name_b}** possui **{val_b['Classes']}** classes e **{val_b['Funções']}** funções.")


    st.subheader("🌐 Score Arquitetural Final")
    fig_score = px.bar(df_summary, x='Score Final', y='Projeto', orientation='h', color='Projeto',
                       title='Pontuação Arquitetural Global (0–100)', text='Score Final')
    fig_score.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig_score, use_container_width=True)


    st.subheader("📈 Radar de Comparação Geral (Ponderado)")
    categories = ['manutenibilidade', 'complexidade', 'coupling', 'structure']
    
    try:
        # --- MUDANÇA AQUI ---
        # Multiplica o score (0-100) pelo peso (0-1) para mostrar a *contribuição* da métrica
        radar_a = [scores_a[m] * weights.get(m, 0) for m in categories]
        radar_b = [scores_b[m] * weights.get(m, 0) for m in categories]
        # --- FIM DA MUDANÇA ---
        
        radar_df = pd.DataFrame({
            'Métrica': categories + categories,
            'Valor Ponderado': radar_a + radar_b,
            'Projeto': [name_a]*len(categories) + [name_b]*len(categories)
        })
        
        # --- MUDANÇA AQUI ---
        # O eixo 'r' agora é 'Valor Ponderado'
        fig_radar = px.line_polar(radar_df, r='Valor Ponderado', theta='Métrica', color='Projeto', line_close=True)
        # --- FIM DA MUDANÇA ---
        
        st.plotly_chart(fig_radar, use_container_width=True)
    except KeyError as e:
        st.error(f"❌ Erro ao gerar gráfico Radar: a chave {e} está faltando nos scores.")
        st.write("Verifique a saída da função `compute_scores`.")


    # === Conclusão ===
    st.subheader("🧾 Análise Automática (Score Final)")
    winner_name = ""
    loser_name = ""
    if scores_a['final_score'] > scores_b['final_score']:
        winner_name = name_a # Projeto DDD
        loser_name = name_b # Projeto Tradicional
        st.success(f"✅ O **{winner_name}** apresentou melhor score geral ({scores_a['final_score']:.1f}), indicando maior qualidade arquitetural.")
    elif scores_b['final_score'] > scores_a['final_score']:
        winner_name = name_b # Projeto Tradicional
        loser_name = name_a # Projeto DDD
        st.success(f"✅ O **{winner_name}** apresentou melhor score geral ({scores_b['final_score']:.1f}), indicando maior qualidade arquitetural.")
    else:
        st.warning("⚖️ Ambos os projetos tiveram scores equivalentes — recomenda-se inspeção qualitativa.")
    
    st.info("As métricas visuais permitem compreender como o DDD influencia modularidade, acoplamento e manutenção.")

    # === CONCLUSÃO GERAL (NOVO) ===
    # Esta seção agora sabe qual projeto é qual (name_a é DDD, name_b é Tradicional)
    st.subheader("🏁 Conclusão Geral e Recomendações")
    
    ddd_context_text = ""
    
    if not winner_name:
        # Caso de empate
        ddd_context_text = "Ambos os projetos apresentaram scores finais equivalentes. Uma análise qualitativa é necessária para determinar a melhor abordagem para o seu contexto de e-commerce."
    
    elif winner_name == name_a: # Se "Projeto DDD" venceu
        score_diff = abs(scores_a['final_score'] - scores_b['final_score'])
        ddd_context_text = f"""
        A análise de métricas quantitativas indicou que o **{name_a}** venceu, superando o **{name_b}** por **{score_diff:.1f}** pontos.
        
        **Contexto (DDD Venceu):**
        
        Os dados sugerem que a abordagem DDD foi **bem-sucedida** em criar uma arquitetura de maior qualidade, conforme as métricas. Isso é provavelmente visível em:
        * **Menor Acoplamento:** Os módulos (Bounded Contexts) são mais independentes.
        * **Maior número de Domínios Detectados:** A separação de responsabilidades está mais clara.
        * **Maior Índice de Manutenibilidade (MI):** O código é mais fácil de manter, apesar de talvez ser maior (mais LOC).
        
        **Recomendação:** O resultado quantitativo é positivo. Aconselha-se agora focar na análise qualitativa para garantir que a coesão e a clareza da "Linguagem Ubiqua" também estão presentes.
        """
        
    elif winner_name == name_b: # Se "Projeto Tradicional" venceu
        score_diff = abs(scores_a['final_score'] - scores_b['final_score'])
        ddd_context_text = f"""
        A análise de métricas quantitativas indicou que o **{name_b}** venceu, superando o **{name_a}** por **{score_diff:.1f}** pontos.
        
        **Contexto (Tradicional Venceu):**
        
        Ver o projeto Tradicional vencer **não é necessariamente ruim**, mas levanta questões importantes sobre a implementação do DDD:
        * O projeto DDD pode estar sofrendo de ***over-engineering*** (complexidade desnecessária para o problema).
        * A implementação do DDD pode estar **falha**, resultando em alto acoplamento ou baixa coesão (ex: "Anemic Domain Model").
        * Alternativamente, a arquitetura tradicional pode ser simplesmente mais madura, simples e bem refatorada, sendo mais adequada para o escopo.
        
        **Recomendação:** Use esta análise para investigar *por que* o projeto DDD teve um score menor. Verifique se o custo da complexidade do DDD está trazendo benefícios qualitativos (clareza de negócio) que as métricas não capturam.
        """

    st.markdown(ddd_context_text) # Exibe o texto da conclusão
    
    # Adiciona a recomendação final
    st.markdown("""
    ---
    **Nota Final:** Use esta análise como ponto de partida. O "melhor" projeto (especialmente em DDD) também é definido pela **coesão** (lógica de negócio agrupada) e pela **clareza** com que o código reflete a linguagem de negócio (Linguagem Ubiqua), métricas que esta ferramenta não mede qualitativamente.
    """)


    # Expander para debug e pesos
    with st.expander("📂 Ver dados JSON recebidos (Debug)"):
        st.json({"Projeto 1": metrics_a, "Projeto 2": metrics_b})
        st.json({"Scores (0-100) Projeto 1": scores_a, "Scores (0-100) Projeto 2": scores_b})
        st.json({"Pesos Aplicados (Normalizados)": weights})

def save_json_report(output_path, payload):
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return str(p)