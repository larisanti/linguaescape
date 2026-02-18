from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Literal

# Schema dos exercícios
class Exercise(BaseModel):
    """
    Representa um único bloco de exercício gerado pela IA.
    Esta classe garante que a resposta da IA tenha sempre os mesmos campos.
    """
    exercise_type: str = Field(..., description="Type of exercise generated.")
    instruction: str = Field(..., description="Instruction for the student.")
    content: List[str] = Field(..., description="List of questions or sentences.")
    options: Optional[List[List[str]]] = Field(None, description="List of options for each question.")
    answer_key: str = Field(..., description="Correct answer.")

# Schema de request
class ExerciseRequest(BaseModel):
    """
    Este é o filtro de entrada. Se o JSON enviado pelo Streamlit não bater
    exatamente com estas definições, o Pydantic bloqueia a requisição antes de chegar na IA.
    """
    theme: str = Field(..., example="Vocabulary set. Ex: Technology")
    topic: str = Field(..., example="Grammar topic. Ex: Future with Will")
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] = Field(...)
    age_group: Literal["Kids", "Teens", "Adults"] = Field(...)

    # Quantidade de blocos por tipo de exercício (contagem)
    gap_fill_count: int = Field(0, ge=0, le=10, description="Quantity of Gap Fill exercises.")
    sentence_formation_count: int = Field(0, ge=0, le=10, description="Quantity of Sentence Formation exercises.")
    multiple_choice_count: int = Field(0, ge=0, le=10, description="Quantity of Multiple Choice exercises.")
    
    # Quantidade itens por tipo de exercício (densidade)
    gap_fill_items: int = Field(0, ge=0, le=10, description="Items per Gap Fill block")
    sentence_formation_items: int = Field(0, ge=0, le=10, description="Items per Sentence Formation block")
    multiple_choice_items: int = Field(0, ge=0, le=10, description="Items per Multiple Choice block")
    required_words: Optional[List[str]] = Field(default=None)

    # Validação da lógica de negócio e consistência dos dados
    @model_validator(mode='after')
    def check_total_exercises(self):
        """
        Executa após as validações individuais. Aqui checamos a relação entre os campos.
        """
        total = self.gap_fill_count + self.sentence_formation_count + self.multiple_choice_count
        
        # Regra 1: Não pode ser tudo zero
        if total == 0:
            raise ValueError("You must request at least one exercise of any type.")
        
        # Regra 2: Total de exercícios não pode ultrapassar 10
        if total > 10: 
            raise ValueError("Too many exercises! The maximum total is 10.")
            
        # Regra 3: Impede a criação de um bloco vazio
        if (self.gap_fill_count > 0 and self.gap_fill_items == 0) or \
           (self.sentence_formation_count > 0 and self.sentence_formation_items == 0) or \
           (self.multiple_choice_count > 0 and self.multiple_choice_items == 0):
            raise ValueError("You selected an exercise block but left the number of questions at 0.")
        
        return self

# Schema de response
class ExerciseResponse(BaseModel):
    """
    Define a estrutura final que a API devolve.
    O título é montado no Python, e os exercícios vêm da IA.
    É o objeto que o pdf_generator.py recebe para desenhar o documento.
    """
    title: str = Field(..., description="Auto-generated title: 'Topic - Theme'")
    exercises: List[Exercise] = Field(..., min_items=1, max_items=10)
    cefr_descriptors: Optional[str] = Field(default=None, description="Official CEFR descriptors used for pedagogical alignment.")