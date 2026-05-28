import customtkinter as ctk
import tkinter as tk
import ctypes
import sys
import platform
import warnings

warnings.filterwarnings("ignore", category=UserWarning)  # remove aviso do VS Code no terminal

from pathlib import Path
from functions import CarregarArquivo


ctk.set_appearance_mode("dark")

class GerenciadorIcone:

    _icone_global = None  # mantém referência global

    @staticmethod
    def aplicar_icone(janela):

        # ---- SUBSTITUA A LINHA ANTIGA POR ESTE BLOCO ----
        import os  # Garanta que o os está importado se não estiver no topo
        if "APPDIR" in os.environ:
            BASE_DIR = Path(os.environ["APPDIR"])
        else:
            BASE_DIR = Path(__file__).parent.resolve()
        # ------------------------------------------------

        sistema = platform.system()

        try:
            # WINDOWS
            if sistema == "Windows":
                icone = BASE_DIR / "assets" / "docpdf.ico"
                if icone.exists():
                    janela.iconbitmap(str(icone))

            # LINUX / MAC
            else:
                icone = BASE_DIR / "assets" / "docpdf.png"
                if icone.exists():
                    # cria apenas uma vez
                    if GerenciadorIcone._icone_global is None:
                        GerenciadorIcone._icone_global = tk.PhotoImage(
                            file=str(icone)
                        )
                    janela.iconphoto(
                        True,
                        GerenciadorIcone._icone_global
                    )
            print("Ícone carregado com sucesso!")

        except Exception as e:
            print("Erro ao carregar ícone:", e)

class PopupSobre(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        # Configuração básica da janela popup:
        self.title("Sobre o app")
        self.attributes("-topmost", True)
        self.configure(bg="#2C2C2C")

        # Inserir ícone na barra de título:
        GerenciadorIcone.aplicar_icone(self)

        # Ativa barra de título escura (Windows):
        if sys.platform.startswith("win"):
            self.after(10, self.ativar_dark_titlebar)

        # Configuração para bloquear interface:
        # self.transient(master)
        # self.grab_set()        * no linux esse método não funciona
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.fecha_popup)  # devolve domínio para janela principal

        # Configuração de tamanho-centralização:
        popup_width, popup_height = 350, 180

        tela_width = self.winfo_screenwidth()
        tela_height = self.winfo_screenheight()
        x = (tela_width // 2) - (popup_width // 2)
        y = (tela_height // 2) - (popup_height // 2)

        self.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        self.resizable(False, False)

        # Remove minimizar/maximizar (Windows)
        if sys.platform.startswith("win"):
            GWL_STYLE = -16
            WS_MINIMIZEBOX = 0x00020000
            WS_MAXIMIZEBOX = 0x00010000
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style &= ~WS_MINIMIZEBOX
            style &= ~WS_MAXIMIZEBOX
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            ctypes.windll.user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                0x0002 | 0x0001 | 0x0040 | 0x0020
            )

        # Conteúdo da janela:
        info = (
            "Leitor para arquivos PDF\n\n"
            "Renderização de PDF em imagem RGB\n"
            "Interface: Python + CustomTkinter\n"
            "Desenvolvedor: Danilo dos Santos Soares\n"
            "Contato: (11) 9 4138-3504\n\n"
            "© 2026 - Todos os direitos reservados."
        )

        label_info = ctk.CTkLabel(
            master=self,
            text=info,
            justify="left",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14)
        )
        label_info.pack(padx=20, pady=20)

    # Função para alterar barra de título:
    def ativar_dark_titlebar(self):
        self.update()
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        valor = ctypes.c_int(1)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(valor),
            ctypes.sizeof(valor)
        )

    def fecha_popup(self):
        self.destroy()

class Interface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Leitor PDF")
        # self.attributes("-topmost", True)        * recurso opcional
        self.resizable(True, True)

        # Inserindo ícone:
        GerenciadorIcone.aplicar_icone(self)

        # Configuração de tamanho-centralização:
        app_width, app_height = 900, 580

        tela_width = self.winfo_screenwidth()
        tela_height = self.winfo_screenheight()
        x = (tela_width // 2) - (app_width // 2)
        y = (tela_height // 2) - (app_height // 2) - 30  # ajuste fino (levantar um pouco no eixo y)

        self.geometry(f"{app_width}x{app_height}+{x}+{y}")

        # Cria o scroll_frame, mas NÃO posiciona (fica oculto)
        self.scroll_frame = ctk.CTkScrollableFrame(
            master=self,
            width=850, 
            height=500
        )

        # Compatibilidade de scroll Linux
        self.bind_all("<Button-4>", self._scroll_linux)
        self.bind_all("<Button-5>", self._scroll_linux)

        # Botão:
        self.btn_carregar = ctk.CTkButton(
            master=self,
            text="Carregar PDF",
            width=100,
            height=28,
            fg_color="#D60707",
            hover_color="#494444",
            corner_radius=6,
            command=self.carregar_pdf
        )
        self.btn_carregar.place(
            relx=0.5,      # mesma margem do frame             *alinhamento à esquerda: relx=0.03
            rely=0.023,    # mantém seu espaçamento do topo    *alinhamento à esquerda: rely=0.023
            anchor=ctk.N   # centralização absoluta            *alinhamento à esquerda: anchor=ctk.NW
        )

        # Link para janela de informação
        self.info_sobre = ctk.CTkLabel(
            master=self,
            text="Sobre",
            text_color="#999292",
            cursor="hand2",
            font=ctk.CTkFont(size=13)
        )
        self.info_sobre.place(
            relx=0.97,
            rely=0.023,
            anchor=ctk.NE
        )
        self.info_sobre.bind("<Button-1>", lambda e: PopupSobre(self))  # abre janela popup

        # Instância da classe de carregamento:
        self.loader = CarregarArquivo()

    # Função para carregar arquivo:
    def carregar_pdf(self):

        # Tenta carregar primeiro:
        carregou = self.loader.carregar(self.scroll_frame, self)

        # Mostra o frame se realmente carregou:
        if carregou:
            self.scroll_frame.place(
                relx=0.5,        # 50% da largura - centraliza horizontalmente
                rely=0.09,       # controla espaço do topo
                anchor=ctk.N,    # o frame "gruda" pelo topo
                relwidth=0.96,   # 96% da largura da janela
                relheight=0.88   # ajusta para não estourar embaixo
            )

    # Evita erro se o frame ainda não estiver visível
    def _scroll_linux(self, event):

        if not self.scroll_frame.winfo_ismapped():
            return

        if event.num == 4:
            self.scroll_frame._parent_canvas.yview_scroll(-1, "units")

        elif event.num == 5:
            self.scroll_frame._parent_canvas.yview_scroll(1, "units")


if __name__ == "__main__":
    app = Interface()
    app.mainloop()