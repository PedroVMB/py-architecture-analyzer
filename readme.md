# 🏗️ Comparador Arquitetural: DDD vs Não-DDD (E-commerce)

Este projeto foi desenvolvido como parte de um **Trabalho de Conclusão de Curso (TCC)** na área de **Engenharia de Software**, com o objetivo de **comparar arquiteturas de software em projetos de e-commerce** desenvolvidos em Python, utilizando **Domain-Driven Design (DDD)** e uma arquitetura tradicional **sem DDD (CRUD/monolítica)**.

A aplicação permite analisar dois repositórios GitHub ou arquivos ZIP de projetos e calcular métricas de qualidade de software, gerando relatórios comparativos.

---

## 📌 Funcionalidades

- Upload de **dois projetos** via:
  - URL do GitHub (públicos ou privados com token).
  - Upload direto de arquivos ZIP.
- Extração de métricas de engenharia de software:
  - **Linhas de Código (LOC)**
  - **Número de classes, funções e módulos**
  - **Complexidade Ciclomática** (via [radon](https://github.com/rubik/radon))
  - **Índice de Manutenibilidade**
  - **Acoplamento entre módulos**
- Comparação visual:
  - **Tabelas comparativas**
  - **Gráfico radar** mostrando forças e fraquezas de cada projeto.
- Geração de relatório com **insights automáticos**.

---

## 📊 Repositórios de Exemplo Utilizados

Para a análise proposta no TCC, sugerimos os seguintes repositórios públicos:

**DDD (com Domain-Driven Design)**  
🔗 [pgorecki/python-ddd](https://github.com/pgorecki/python-ddd)

**Sem DDD (arquitetura tradicional)**  
🔗 [codingforentrepreneurs/eCommerce](https://github.com/codingforentrepreneurs/eCommerce)  
*(se apresentar erro no branch `main`, usar [django-beginners-ecommerce](https://github.com/sibtc/django-beginners-ecommerce))*  

---

## ⚙️ Instalação e Execução

### 1. Clonar este repositório
```bash
git clone https://github.com/seu-usuario/architecture-compare.git
cd architecture-compare
```
### 2. Criar e ativar um ambiente virtual
```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```
### 3. Instalar dependências
```bash
pip install -r requirements.txt
```
### 4. Executar a aplicação
```bash 
streamlit run app.py
```
### Acesse em: 
http://localhost:8501

## 📈 Exemplo de Uso

Forneça os links de dois repositórios (um com DDD, outro sem DDD).

Ajuste os pesos das métricas (manutenibilidade, complexidade, acoplamento).

Clique em Rodar Análise.

Veja os resultados em tabelas e gráficos radar.

## 📚 Base Teórica

A análise se fundamenta em métricas de qualidade de software (ISO/IEC 25010), destacando:

Manutenibilidade

Complexidade

Modularidade

Testabilidade

O projeto contribui com uma forma prática de comparar arquiteturas, evidenciando vantagens do DDD em sistemas de e-commerce.

## 📚  Testes

Para rodar os testes da aplicação, basta utilizar o comando no diretório raiz da aplicação

```bash
PYTHONPATH=. pytest -v       
```

Esses testes seguem o princípio de verificação de consistência das métricas de software, que visa confirmar se os indicadores computados correspondem a propriedades mensuráveis da arquitetura.
As principais referências que sustentam isso são:

Wohlin, C. et al. (2012) — Experimentation in Software Engineering, Springer.
→ Defende o uso de testes automatizados como meio de validação empírica de métricas de software.

IEEE Std 982.1-1988 — IEEE Guide for the Application of Software Reliability Models.
→ Aponta a importância da confiabilidade de medidas para estudos comparativos.

Basili & Weiss (1984) — A Methodology for Collecting Valid Software Engineering Data.
→ Define a importância da rastreabilidade e validade dos dados coletados.

## 👨‍💻 Tecnologias Utilizadas

- Python 3.13+

- Streamlit
   (UI interativa)

- Radon
   (complexidade e manutenibilidade)

- Pylint
   (análise estática)

- Requests
   (integração com GitHub API)

- Plotly
   (gráficos radar)

## 📜 Licença

Este projeto é de uso acadêmico.
Você pode utilizá-lo como base para estudos e trabalhos educacionais.

## ✨ Autor

Projeto desenvolvido para TCC de Ciência da Computação

👤 Pedro Vinicius Mota Barreiro

 📧 Email: pedromb.dev@gmail.com