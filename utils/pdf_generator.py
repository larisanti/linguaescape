import os
import sys
import re
from fpdf import FPDF
from schemas import ExerciseResponse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class LinguaescapePDF(FPDF):
    def __init__(self, exercise_title):
        super().__init__()
        self.exercise_title = exercise_title
        
        # Margem
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=25) 
        
        # Fonte
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        font_dir = os.path.join(base_dir, 'font')
        
        self.add_font('Atkinson', '', os.path.join(font_dir, 'AtkinsonHyperlegible-Regular.ttf'))
        self.add_font('Atkinson', 'B', os.path.join(font_dir, 'AtkinsonHyperlegible-Bold.ttf'))
        self.add_font('Atkinson', 'I', os.path.join(font_dir, 'AtkinsonHyperlegible-Italic.ttf'))
        self.add_font('Atkinson', 'BI', os.path.join(font_dir, 'AtkinsonHyperlegible-BoldItalic.ttf'))
        
        self.header_img = os.path.join(base_dir, 'images', 'linguaescape-header.png')
        self.footer_img = os.path.join(base_dir, 'images', 'linguaescape-footer.png')

    # Header e footer
    def header(self):
        if self.page_no() == 1:
            if os.path.exists(self.header_img):
                self.image(self.header_img, x=0, y=0, w=210)
                self.set_y(65) 
            else:
                self.set_y(15)
        else:
            self.set_y(15)

        self.set_font("Atkinson", "B", 14)
        self.cell(0, 10, self.exercise_title, ln=True, align="C")
        self.ln(8)

    def footer(self):
        if os.path.exists(self.footer_img):
            altura_rodape_mm = 15 
            self.image(self.footer_img, x=0, y=297 - altura_rodape_mm, w=210)
        else:
            self.set_y(-15)
            self.set_font("Atkinson", "I", 11)
            self.cell(0, 10, "Linguaescape", align="R")

# Função para gerar o PDF a partir do objeto de resposta
def generate_pdf_bytes(data: ExerciseResponse):
    pdf = LinguaescapePDF(exercise_title=data.title)
    pdf.add_page()

    # Renderização dos exercícios
    for i, ex in enumerate(data.exercises):
        
        pdf.set_font("Atkinson", "B", 11)
        clean_instruction = ex.instruction.replace("Instruction:", "").strip()
        pdf.multi_cell(0, 8, f"{i+1}. {clean_instruction}")
        pdf.ln(2) 

        pdf.set_font("Atkinson", "", 11)
        for idx, sentence in enumerate(ex.content):
            
            if ex.exercise_type == "Gap Fill":
                sentence = re.sub(r'_+', '_________________________', sentence)
            
            pdf.multi_cell(0, 8, f"{idx+1}. {sentence}")
            
            # Formatação das alternativas de Multiple Choice
            if ex.exercise_type == "Multiple Choice" and ex.options:
                pdf.set_font("Atkinson", "", 11)
                
                # Margem para as opções
                for opt in ex.options[idx]:
                    clean_opt = opt.replace('\n', '').strip()
                    pdf.set_x(20)
                    pdf.multi_cell(0, 7, clean_opt)
                
                pdf.ln(4) # Respiro antes do próximo bloco
            
            # Formatação para Sentence Formation
            elif ex.exercise_type == "Sentence Formation":
                pdf.set_x(20) 
                pdf.set_font("Helvetica", "", 11)
                pdf.cell(0, 8, "____________________________________________________________________", ln=True)
                pdf.set_font("Atkinson", "", 11)

            if ex.exercise_type == "Gap Fill":
                pdf.ln(4)
            else:
                pdf.ln(2)
        
        pdf.ln(8) 

    # Answer Key 
    pdf.add_page()
    pdf.set_font("Atkinson", "B", 14)
    pdf.cell(0, 10, "Answer Key", ln=True, align="C")
    pdf.ln(8)
    
    for i, ex in enumerate(data.exercises):
        answers = [ans.strip() for ans in ex.answer_key.split(";") if ans.strip()]
        
        pdf.set_font("Atkinson", "B", 11)
        pdf.cell(0, 8, f"Exercise {i+1}:", ln=True)
        
        pdf.set_font("Atkinson", "", 11)
        for ans in answers:
            pdf.cell(0, 7, ans, ln=True)
        
        pdf.ln(6)

    # CEFR Descriptors
    if hasattr(data, 'cefr_descriptors') and data.cefr_descriptors:
        pdf.add_page()
        
        pdf.set_font("Atkinson", "I", 11)
        pdf.multi_cell(0, 6, "The exercises were generated following the CEFR descriptors below:")
        pdf.ln(6)
        
        pdf.set_font("Atkinson", "", 11)
        
        linhas_descritores = data.cefr_descriptors.split('\n')
        for linha in linhas_descritores:
            if linha.strip(): 
                pdf.multi_cell(0, 7, linha.strip())
                pdf.ln(2) 

    return bytes(pdf.output())