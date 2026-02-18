![Logo Linguaescape](images/logotipos/2.png)

O **Linguaescape** é uma aplicação inteligente desenvolvida para automatizar a criação de recursos educacionais para o ensino de língua inglesa. O projeto une Inteligência Artificial Generativa com os requisitos do Quadro Europeu Comum de Referência para Línguas (**CEFR**), permitindo que professores gerem exercícios personalizados e prontos para impressão em segundos.

<br>


## Ponto Principais
* Alinhamento Pedagógico (RAG): Implementação de técnica de Retrieval-Augmented Generation para fundamentar a criação de exercícios em descritores oficiais do CEFR, garantindo que a IA gere materiais com alto rigor pedagógico e sem alucinações de nível linguístico.
* Design Acessível: Integração da tipografia Atkinson Hyperlegible (desenvolvida pelo Braille Institute) na geração dinâmica de PDFs, focando em máxima legibilidade e inclusão.
* Arquitetura de Microsserviços e DevOps: Estrutura desacoplada entre Frontend (Streamlit) e Backend (FastAPI), facilitando a manutenção, escalabilidade e permitindo deploys independentes via containers Docker.

<br>


## Tecnologias Utilizadas
* **Linguagem:** Python 3.13.11
* **IA & NLP:** Google Gemini 2.0/2.5 Flash (via `google-genai`)
* **Frontend:** Streamlit
* **Backend:** FastAPI & Uvicorn (Arquitetura Assíncrona)
* **Validação:** Pydantic (Garantia de tipos e contratos de dados/schemas)
* **Processamento de Dados:** Pandas & Openpyxl (Engenharia de dados para RAG)
* **Geração de Documentos:** fpdf2 (Criação dinâmica de PDFs)
* **DevOps:** Docker & Docker Compose (Containerização e Orquestração de serviços)

<br>


## Estrutura de Pastas

```text
linguaescape-ai/
├── data/              
├── font/              
├── images/             
├── utils/              # Lógica de RAG (cefr_rag.py) e gerador de PDF (pdf_generator.py)
├── app.py              # Interface do usuário (Streamlit)
├── main.py             # Ponto de entrada da API (FastAPI)
├── router.py           # Definição das rotas e endpoints
├── services.py         # Integração com a IA e lógica de Agente Semântico
├── schemas.py          # Modelos de dados e validações Pydantic
├── requirements.txt    
├── Dockerfile          
└── docker-compose.yml 
