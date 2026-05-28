import customtkinter as ctk
import fitz  # PyMuPDF
import os
from PIL import Image
from tkinter import filedialog

class CarregarArquivo():
    def carregar(self, scroll_frame, parent):
        # Força o diálogo a abrir na Home do usuário Linux
        diretorio_inicial = os.path.expanduser("~")
        
        caminho = filedialog.askopenfilename(
            parent=parent,
            initialdir=diretorio_inicial,
            filetypes=[("Arquivos PDF", "*.pdf")]
        )

        if not caminho:
            return False

        # Garante o caminho absoluto real do sistema
        caminho_absoluto = os.path.abspath(caminho)

        # Limpa os widgets antigos do frame de scroll (se houver)
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        try:
            # Abre o documento PDF de forma segura
            doc = fitz.open(caminho_absoluto)
            
            # Mantém uma referência das imagens para o Tkinter não apagar da memória
            scroll_frame.imagens_pdf = []

            for numero_pagina in range(len(doc)):
                pagina = doc.load_page(numero_pagina)
                
                # ---- AJUSTE DE ZOOM E TAMANHO MAIOR ----
                # Aumenta a resolução da renderização para manter o texto nítido
                fator_zoom = 2.2 
                matriz = fitz.Matrix(fator_zoom, fator_zoom)
                pix = pagina.get_pixmap(matrix=matriz)
                
                # Converte os bytes do PyMuPDF para PIL Image
                imagem_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Define o tamanho de exibição expandido na interface (proporção maior)
                largura_tela = int(pix.width // (fator_zoom / 1.5))
                altura_tela = int(pix.height // (fator_zoom / 1.5))
                
                imagem_ctk = ctk.CTkImage(
                    light_image=imagem_pil, 
                    dark_image=imagem_pil, 
                    size=(largura_tela, altura_tela)
                )
                # ----------------------------------------
                
                scroll_frame.imagens_pdf.append(imagem_ctk)

                # Cria o label para exibir a página maior
                label_pagina = ctk.CTkLabel(master=scroll_frame, image=imagem_ctk, text="")
                label_pagina.pack(pady=15, padx=10)

            print("PDF carregado com sucesso!")
            
            return True
                    

        except Exception as e:
            print(f"Erro ao renderizar o PDF no AppImage: {e}")
            return False
