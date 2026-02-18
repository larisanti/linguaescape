# filtro determinístico e sintático

import os
import pandas as pd

def get_cefr_context(target_level: str) -> str:
    """
    Lê o arquivo Excel do CEFR local, filtra pelo nível (incluindo as versões '+'),
    ignora descritores vazios ("No descriptors available") e retorna os textos.
    """
    # 1. Caminho dinâmico para achar a pasta 'data' na raiz do projeto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    excel_path = os.path.join(base_dir, 'data', 'CEFR Descriptors (2020).xlsx')

    # 2. Carrega a planilha Excel
    try:
        df = pd.read_excel(excel_path)
    except FileNotFoundError:
        return f"Warning: CEFR database not found at {excel_path}. Generating without specific constraints."
    except Exception as e:
        return f"Warning: Error reading the Excel file: {str(e)}"

    # 3. As categorias cirúrgicas que você mapeou
    categorias_alvo = [
        'Grammatical accuracy', 
        'Vocabulary control', 
        'Vocabulary range', 
        'Orthographic control',
        'General linguistic range',
        'Propositional precision',
        'Overall reading comprehension',
        'Identifying cues and inferring (spoken, signed and written)',
        'Overall written production'
    ]

    # 4. Agrupamento Inteligente de Níveis (RAG Tabular Avançado)
    # Cria uma lista com o nível exato e a versão "Plus" (Ex: ["A2", "A2+"])
    niveis_aceitos = [target_level, f"{target_level}+"]

    # 5. Filtro Triplo
    # - Filtra pelo 'Level' checando se está na nossa lista de niveis_aceitos
    # - Filtra pelas categorias em 'Scale'
    # - Ignora qualquer linha na coluna 'Descriptor' que contenha "No descriptors available"
    df_filtrado = df[
        (df['Level'].isin(niveis_aceitos)) & 
        (df['Scale'].isin(categorias_alvo)) &
        (~df['Descriptor'].astype(str).str.contains("No descriptors available", case=False, na=False))
    ]

    # Se não achar nada para aquele nível após os filtros, retorna um aviso
    if df_filtrado.empty:
        return f"No specific descriptors found for level {target_level} in the selected categories."

    # 6. Extrai os textos (coluna 'Descriptor') e formata como lista
    lista_descritores = df_filtrado['Descriptor'].dropna().tolist()
    contexto_formatado = "\n".join([f"- {desc}" for desc in lista_descritores])
    
    return contexto_formatado