import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from schemas import ExerciseRequest, ExerciseResponse, Exercise, AIOutput
from pydantic import BaseModel, Field 
from typing import List
from utils.cefr_rag import get_cefr_context

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_exercises(data: ExerciseRequest) -> ExerciseResponse:
    """
    Função principal do serviço.
    Entrada: O pedido validado do professor (ExerciseRequest).
    Saída: A resposta estruturada pronta para o front-end (ExerciseResponse).
    """
    # Título só com python pra padronizar e economizar tokens
    final_title = f"{data.topic} - {data.theme}"

    # Calcula o total de atividades para focar a atenção da IA na quantidade certa
    total_count = data.gap_fill_count + data.sentence_formation_count + data.multiple_choice_count

    # RAG tabular: Busca os descritores exatos para o nível selecionado
    cefr_descriptors = get_cefr_context(data.level)

    # Agente Semântico: O modelo analisa o conteúdo gerado e seleciona os descritores
    prompt = f"""
    - You are an EFL Teacher and Curriculum Developer. 
    - Your expertise lies in crafting highly accurate, engaging, and context-rich learning materials strictly calibrated to the CEFR framework. 
    - You design exercises that are pedagogically sound, using natural, authentic English rather than outdated or robotic textbook phrasing.

    Create a list of exercises for {data.age_group} students (Level {data.level}).
    
    Context: {data.theme} | Topic: {data.topic}
    
    ### CEFR ALIGNMENT:
    You MUST strictly align the vocabulary, grammar complexity, reading comprehension, and overall difficulty of ALL exercises to these official CEFR {data.level} descriptors:
    {cefr_descriptors}
    
    >>> EXTRACTION TASK: After generating the exercises, select exactly 3 to 5 descriptors from the list above that best justify your pedagogical choices for this specific topic. Return them exactly as written in the 'used_cefr_descriptors' field. <<<
    
    ### STRUCTURE REQUIREMENTS:
    1. Generate EXACTLY {total_count} distinct exercise blocks.
    2. Distribution and Density:
       - {data.gap_fill_count} Gap Fill (Each block MUST have EXACTLY {data.gap_fill_items} sentences).
       - {data.sentence_formation_count} Sentence Formation (Each block MUST have EXACTLY {data.sentence_formation_items} items).
       - {data.multiple_choice_count} Multiple Choice (Each block MUST have EXACTLY {data.multiple_choice_items} questions).
    
    ### FORMATTING RULES:
    1. The "content" field MUST be a LIST of strings (one string per item).
    2. For Multiple Choice: You MUST generate EXACTLY 4 options (A, B, C, D) per question. The "options" field MUST be a LIST OF LISTS. 
      Example: [ ["A) apple", "B) ball", "C) car", "D) dog"], ["A) cat", "B) dog", "C) cow", "D) bird"] ]
    3. Do NOT group all sentences into a single string. Separate them.

    ### CONTENT RULES:
    1. Use vocabulary appropriate for {data.level} {data.age_group}.
    2. Mandatory keywords: {", ".join(data.required_words) if data.required_words else "None"}.
    3. Provide the correct Answer Key for ALL items generated within each block.
    4. For each Multiple Choice question, the correct answer must be chosen independently. 
    5. Select the correct option for each question completely at RANDOM.
    6. Ensure distractor options are plausible but incorrect.
    7. Format the "answer_key" field as a clear, numbered list separated by semicolons. 
       Example: "1. will; 2. won't; 3. will be".
    """

    print(f"--- Calling Gemini for: '{final_title}' ---")

    # Chamada à API
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIOutput,
                temperature=0.8
            )
        )
        
        # --- PÓS-PROCESSAMENTO DA RESPOSTA ---
        # Filtro semântico para garantir que a IA não inventou descritores ou parafraseou os existentes
        descritores_validados = []
        
        # Descritores que a IA diz ter usado para justificar as escolhas pedagógicas do material
        for desc_ia in response.parsed.used_cefr_descriptors:
            desc_limpo = desc_ia.strip()
            
            # Verificar se o descritor selecionado pela IA realmente existe na base
            if desc_limpo in cefr_descriptors:
                descritores_validados.append(f"- {desc_limpo}")
            else:
                # Descartar a frase e apresentar erro se a IA inventar ou parafrasear
                print(f"ALERTA DE ALUCINAÇÃO BLOQUEADO: A IA tentou alterar o descritor: {desc_limpo}")
                
        # Join com quebras de linha para enviar a string formatada para o fpdf gerar a página
        selected_desc_str = "\n".join(descritores_validados)
        
        # Merge título e exercícios em um único objeto de resposta para o frontend
        return ExerciseResponse(
            title=final_title,
            exercises=response.parsed.exercises,
            cefr_descriptors=selected_desc_str
        )

    except Exception as e:
        print(f"Error in AI Service: {e}")
        raise e