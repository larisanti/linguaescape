from fastapi import APIRouter, HTTPException
from schemas import ActivityRequest, ActivityResponse
from services import generate_activities

# Cria o roteador
router = APIRouter()

@router.post("/generate", response_model=ActivityResponse)
async def generate_lesson_endpoint(request: ActivityRequest):
    """
    Endpoint que recebe o pedido do Streamlit, valida os dados e chama o serviço de IA.
    """
    try:
        # Chama a função no services.py
        result = generate_activities(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))