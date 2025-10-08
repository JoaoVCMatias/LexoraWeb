# pip install customtkinter pillow
import customtkinter as ctk
from PIL import Image

# ---------- Aparência e tema ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- Paleta de Cores ----------
PRIMARY_BLUE   = "#1153BE"
FIELD_BG       = "#F7F8FA"
FIELD_BORDER   = "#E5E7EB"
LABEL_COLOR    = "#4B5563"
SUBTLE         = "#6B7280"
PLACEHOLDER    = "#9AA0A6"

# ---------- Medidas da UI ----------
FORM_WIDTH     = 600
FIELD_HEIGHT   = 46
ROW_GAP_TOP    = 8
ROW_GAP_BOTTOM = 20
ICON_SIZE      = 20
ICON_W         = 40
EYE_W          = 48
INNER_PAD_Y    = 10
SPACER_X       = 20

class SignUpApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lexora — Crie sua conta")
        self.geometry("1280x800")
        self.minsize(1100, 720)
        self.configure(fg_color="#FFFFFF")

        # --- Carregar Ícones e Logo ---
        try:
            # Logo do topo (renomeie seu arquivo para "logo.png")
            self.logo_image = ctk.CTkImage(Image.open("logo.png"), size=(141, 96))
            
            # Ícones dos campos
            self.user_icon        = ctk.CTkImage(Image.open("user.png"),    size=(ICON_SIZE, ICON_SIZE))
            self.mail_icon        = ctk.CTkImage(Image.open("mail.png"),    size=(ICON_SIZE, ICON_SIZE))
            self.lock_icon        = ctk.CTkImage(Image.open("cadeado.png"), size=(ICON_SIZE, ICON_SIZE))
            self.eye_open_icon    = ctk.CTkImage(Image.open("eye.png"),     size=(ICON_SIZE, ICON_SIZE))
            self.eye_slashed_icon = ctk.CTkImage(Image.open("eyef.png"),    size=(ICON_SIZE, ICON_SIZE))
        except FileNotFoundError as e:
            print(f"Erro ao carregar imagem: {e}. Verifique se todos os arquivos estão na pasta.")
            self.logo_image = None 

        # --- Layout Central ---
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True)

        # 1. IMAGEM SUPERIOR CENTRALIZADA
        if self.logo_image:
            ctk.CTkLabel(center, text="", image=self.logo_image, fg_color="transparent").pack(pady=(0, 20))

        # Títulos (sem o texto "Lexora")
        ctk.CTkLabel(center, text="CRIE SUA CONTA", text_color=PRIMARY_BLUE, font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 2))
        ctk.CTkLabel(center, text="Leva menos de um minuto para começar gratuitamente!", text_color=SUBTLE, font=ctk.CTkFont(size=13)).pack(pady=(0, 22))

        # Formulário
        form = ctk.CTkFrame(center, fg_color="transparent", width=FORM_WIDTH)
        form.pack(fill="x", expand=True)

        # Campos de Entrada
        self.nome   = self._input_row(form, "Nome completo",   "Ex: Ana Maria Menezes da Silva", self.user_icon, password=False)
        self.email  = self._input_row(form, "E-mail",          "Ex: nome@email.com",             self.mail_icon, password=False)
        self.senha  = self._input_row(form, "Senha",           "Escolha uma senha segura",       self.lock_icon, password=True)
        self.csenha = self._input_row(form, "Confirmar senha", "Insira a senha escolhida novamente", self.lock_icon, password=True)

        # Botões
        ctk.CTkButton(center, text="Criar conta", width=FORM_WIDTH, height=50, corner_radius=10,
                      fg_color=PRIMARY_BLUE, hover_color="#1153BE").pack(pady=(12, 12))
        ctk.CTkButton(center, text="Já possuo conta", width=FORM_WIDTH, height=44, corner_radius=10,
                      fg_color="#FFFFFF", hover_color="#F3F4F6", text_color=SUBTLE,
                      border_width=1, border_color=FIELD_BORDER).pack()

        # 2. ILUSTRAÇÃO À DIREITA COM FUNDO TRANSPARENTE
        try:
            right_image = ctk.CTkImage(Image.open("ImageM.png"), size=(420, 420))
            ctk.CTkLabel(self, text="", image=right_image, fg_color="transparent").place(relx=1.0, rely=1.0, x=-40, y=-30, anchor="se")
        except FileNotFoundError:
            print("Arquivo 'ImageM.png' não encontrado, a ilustração não será exibida.")

    # ---------- Método para criar uma linha de campo de entrada ----------
    def _input_row(self, parent, label_text, placeholder, icon_image, password=False):
        ctk.CTkLabel(parent, text=label_text, text_color=LABEL_COLOR,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=2)

        wrap = ctk.CTkFrame(parent, height=FIELD_HEIGHT, width=FORM_WIDTH,
                            corner_radius=23, fg_color=FIELD_BG,
                            border_width=1, border_color=FIELD_BORDER)
        wrap.pack(pady=(ROW_GAP_TOP, ROW_GAP_BOTTOM), fill="x")
        wrap.pack_propagate(False)

        wrap.grid_columnconfigure(0, minsize=ICON_W)
        wrap.grid_columnconfigure(1, minsize=SPACER_X)
        wrap.grid_columnconfigure(2, weight=1)
        wrap.grid_columnconfigure(3, minsize=SPACER_X)
        wrap.grid_columnconfigure(4, minsize=(EYE_W if password else 0))

        # 3. ÍCONE COM FUNDO TRANSPARENTE
        ctk.CTkLabel(wrap, image=icon_image, text="", width=ICON_W,
                     anchor="center", fg_color="transparent").grid(row=0, column=0, sticky="nsw", padx=(8, 0))

        ctk.CTkLabel(wrap, text="", width=SPACER_X, fg_color="transparent").grid(row=0, column=1)
        ctk.CTkLabel(wrap, text="", width=SPACER_X, fg_color="transparent").grid(row=0, column=3)

        entry = ctk.CTkEntry(
            wrap, placeholder_text=placeholder, placeholder_text_color=PLACEHOLDER,
            fg_color="transparent", border_width=0,
            height=FIELD_HEIGHT - INNER_PAD_Y,
            font=ctk.CTkFont(size=16), show=""
        )
        entry.grid(row=0, column=2, sticky="nsew", pady=(INNER_PAD_Y // 2, INNER_PAD_Y // 2), padx=(5, 5))

        if password:
            self._make_password_behavior(entry)
            eye_btn = ctk.CTkButton(wrap, image=self.eye_slashed_icon, text="",
                                    width=EYE_W - 12, height=FIELD_HEIGHT - 12,
                                    fg_color="transparent", hover_color="#ECEFF3", corner_radius=6)
            eye_btn.grid(row=0, column=4, sticky="nse", padx=(0, 8))
            eye_btn.configure(command=lambda e=entry, b=eye_btn: self._toggle(e, b))

        return entry

    def _make_password_behavior(self, entry):
        entry.bind("<FocusIn>", lambda e: self._mask_on_focus(entry))
        entry.bind("<FocusOut>", lambda e: self._unmask_if_empty(entry))

    def _mask_on_focus(self, entry):
        if entry.get() == "": entry.configure(show="*")

    def _unmask_if_empty(self, entry):
        if entry.get() == "": entry.configure(show="")

    def _toggle(self, entry, btn):
        if entry.cget("show") == "*":
            entry.configure(show="")
            btn.configure(image=self.eye_slashed_icon)
        else:
            entry.configure(show="*")
            btn.configure(image=self.eye_open_icon)

if __name__ == "__main__":
    app = SignUpApp()
    app.mainloop()
