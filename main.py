from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router

# Cria a aplicação FastAPI
app = FastAPI(
    title="Linguaescape AI",
    description="Generate personalized English exercises with AI",
    version="1.0.0"
)

# Configuração de CORS (Middleware de Segurança)
# Permite que o Streamlit (porta 8501) converse com o FastAPI (porta 8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta as rotas (endpoints) ao app principal
app.include_router(router, prefix="/api/v1")

# Rota root (Health Check) para testar se a API está online
@app.get("/")
def read_root():
    return {"status": "Linguaescape AI is running!"}