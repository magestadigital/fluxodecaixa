# main.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime

# --- PALETA DE CORES E FONTES (Inspirado na imagem de referência) ---
COLOR_BACKGROUND = "#F7F8FA"
COLOR_PANEL = "#FFFFFF"
COLOR_PRIMARY_TEXT = "#1E293B"
COLOR_SECONDARY_TEXT = "#64748B"
COLOR_ACCENT = "#2563EB"
COLOR_ACCENT_HOVER = "#1D4ED8"
COLOR_GREEN = "#16A34A"
COLOR_RED = "#DC2626"
COLOR_BORDER = "#E2E8F0"

FONT_TITLE = ("system", 20, "bold")
FONT_SUBTITLE = ("system", 13, "bold")
FONT_CARD_TITLE = ("system", 11, "bold")
FONT_CARD_VALUE = ("system", 24, "bold")
FONT_NORMAL = ("system", 12)
FONT_BUTTON = ("system", 12, "bold")

class App(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.title("Gestão de Contas")
        self.geometry("1200x750")
        self.minsize(1100, 700)
        self.configure(fg_color=COLOR_BACKGROUND)

        # --- LAYOUT PRINCIPAL ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- CABEÇALHO ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=20)
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_frame, text="Gestão Financeira - Dev Warleandro", font=FONT_TITLE, text_color=COLOR_PRIMARY_TEXT).grid(row=0, column=0, sticky="w")
        
        action_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(action_buttons_frame, text="+ Nova Despesa", command=self.open_add_expense_modal, font=FONT_BUTTON, fg_color=COLOR_RED, hover_color="#B91C1C", height=40).pack(side="left", padx=(0,10))
        ctk.CTkButton(action_buttons_frame, text="+ Nova Receita", command=self.open_add_entry_modal, font=FONT_BUTTON, fg_color=COLOR_GREEN, hover_color="#15803D", height=40).pack(side="left")

        # --- ÁREA DE CONTEÚDO PRINCIPAL ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)

        # --- CARDS DE RESUMO ---
        cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.lbl_saldo = self.create_summary_card(cards_frame, "SALDO ATUAL", "R$ 0,00", COLOR_PRIMARY_TEXT, 0)
        self.lbl_receitas = self.create_summary_card(cards_frame, "RECEITAS (TOTAL)", "R$ 0,00", COLOR_GREEN, 1)
        self.lbl_despesas = self.create_summary_card(cards_frame, "DESPESAS (TOTAL)", "R$ 0,00", COLOR_RED, 2)

        # --- PAINEL DE TRANSAÇÕES ---
        transactions_panel = ctk.CTkFrame(main_frame, fg_color=COLOR_PANEL, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        transactions_panel.grid(row=2, column=0, sticky="nsew")
        transactions_panel.grid_columnconfigure(0, weight=1)
        transactions_panel.grid_rowconfigure(1, weight=1)
        
        panel_header = ctk.CTkFrame(transactions_panel, fg_color="transparent")
        panel_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(10,5))
        ctk.CTkLabel(panel_header, text="Histórico de Transações", font=FONT_SUBTITLE).pack(side="left")
        ctk.CTkButton(panel_header, text="Deletar Selecionado", command=self.delete_selected_item, font=FONT_BUTTON, fg_color="#F1F2F4", text_color=COLOR_SECONDARY_TEXT, hover_color="#E2E6EA").pack(side="right")
        
        self.create_treeview_widget(transactions_panel)
        self.update_all()

    def create_summary_card(self, parent, title, value, color, col):
        card = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        card.grid(row=0, column=col, sticky="ew", padx=(0, 15) if col < 2 else 0)
        ctk.CTkLabel(card, text=title, font=FONT_CARD_TITLE, text_color=COLOR_SECONDARY_TEXT).pack(pady=(15, 5), padx=20, anchor="w")
        lbl_value = ctk.CTkLabel(card, text=value, font=FONT_CARD_VALUE, text_color=color)
        lbl_value.pack(pady=(0, 20), padx=20, anchor="w")
        return lbl_value

    def create_treeview_widget(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLOR_PANEL, foreground=COLOR_PRIMARY_TEXT, fieldbackground=COLOR_PANEL, borderwidth=0, rowheight=40, font=FONT_NORMAL)
        style.configure("Treeview.Heading", font=FONT_BUTTON, background="#F8FAFC", foreground=COLOR_SECONDARY_TEXT, padding=12)
        style.map("Treeview", background=[('selected', COLOR_ACCENT)])
        style.layout("Treeview.Heading", [("Treeview.Heading.cell", {'sticky': 'nswe'})])

        self.tree = ttk.Treeview(parent, columns=('Tipo', 'Descrição', 'Valor', 'Data'), show='headings', style="Treeview")
        self.tree['columns'] = ('db_id', 'db_table', 'Tipo', 'Descrição', 'Valor', 'Data')

        for col in ('Tipo', 'Descrição', 'Valor', 'Data'): self.tree.heading(col, text=col)
        self.tree.column('Tipo', width=100, anchor='center'); self.tree.column('Descrição', width=350); self.tree.column('Valor', width=150, anchor='e'); self.tree.column('Data', width=120, anchor='center')
        for col in ('db_id', 'db_table'): self.tree.column(col, width=0, stretch=False)
        
        self.tree.grid(row=1, column=0, sticky='nsew', padx=20, pady=(5, 20))
        self.tree.tag_configure('receita', foreground=COLOR_GREEN); self.tree.tag_configure('despesa', foreground=COLOR_RED); self.tree.tag_configure('oddrow', background="#F8FAFC")

    def format_currency(self, value): return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def update_all(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        transactions = []
        for r in self.db.buscar_entradas(): transactions.append({'id': r[0], 'table': 'entradas', 'data': r[3], 'type': 'Receita', 'desc': r[1], 'value': r[2], 'tag': 'receita'})
        for s in self.db.buscar_saidas(): transactions.append({'id': s[0], 'table': 'saidas', 'data': s[3], 'type': 'Despesa', 'desc': s[1], 'value': s[2], 'tag': 'despesa'})
        
        transactions.sort(key=lambda x: x['data'], reverse=True)
        
        for i, t in enumerate(transactions):
            row_tag = 'oddrow' if i % 2 == 0 else ''
            date_obj = datetime.fromisoformat(t['data'])
            self.tree.insert("", "end", values=(t['id'], t['table'], t['type'], t['desc'], self.format_currency(t['value']), date_obj.strftime("%d/%m/%Y")), tags=(t['tag'], row_tag))
        
        total_in, total_out, balance = self.db.calcular_totais()
        self.lbl_saldo.configure(text=self.format_currency(balance), text_color=COLOR_GREEN if balance >= 0 else COLOR_RED)
        self.lbl_receitas.configure(text=self.format_currency(total_in))
        self.lbl_despesas.configure(text=self.format_currency(total_out))

    def delete_selected_item(self):
        if not (selected_item := self.tree.selection()):
            messagebox.showwarning("Atenção", "Selecione uma transação para deletar.", parent=self)
            return

        item_values = self.tree.item(selected_item[0], 'values')
        item_id, table_name, desc, value = item_values[0], item_values[1], item_values[3], item_values[4]
        
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar a transação?\n\n'{desc}' - {value}", parent=self):
            self.db.deletar_transacao(table_name, item_id); self.update_all()

    def open_add_entry_modal(self): Modal(self, self.db, "entrada", self.update_all)
    def open_add_expense_modal(self): Modal(self, self.db, "saida", self.update_all)

class Modal(ctk.CTkToplevel):
    def __init__(self, master, db, modal_type, on_close_callback):
        super().__init__(master)
        self.db, self.modal_type, self.on_close = db, modal_type, on_close_callback
        
        is_entry = modal_type == 'entrada'
        self.title(f"Nova {'Receita' if is_entry else 'Despesa'}")
        self.geometry("400x250"); self.resizable(False, False); self.transient(master); self.grab_set()

        ctk.CTkLabel(self, text="Descrição").grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.entry_desc = ctk.CTkEntry(self, font=FONT_NORMAL, width=360); self.entry_desc.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        ctk.CTkLabel(self, text="Valor").grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_valor = ctk.CTkEntry(self, font=FONT_NORMAL, placeholder_text="Ex: 1500,50"); self.entry_valor.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        btn_color = COLOR_GREEN if is_entry else COLOR_RED
        btn_hover = "#15803D" if is_entry else "#B91C1C"
        ctk.CTkButton(self, text="Salvar", command=self.save, font=FONT_BUTTON, fg_color=btn_color, hover_color=btn_hover, height=40).grid(row=4, column=0, padx=20, pady=30, sticky="ew")

    def save(self):
        desc, valor_str = self.entry_desc.get(), self.entry_valor.get().replace(",", ".")
        if not desc or not valor_str: messagebox.showerror("Erro", "Todos os campos são obrigatórios.", parent=self); return
        try: valor = float(valor_str)
        except ValueError: messagebox.showerror("Erro", "O valor deve ser um número válido.", parent=self); return

        if self.modal_type == 'entrada': self.db.adicionar_entrada(desc, valor)
        else: self.db.adicionar_saida(desc, valor)
        
        self.on_close(); self.destroy()

if __name__ == "__main__":
    try: import customtkinter
    except ImportError: messagebox.showerror("Erro de Dependência", "A biblioteca customtkinter não está instalada.\nPor favor, instale usando: pip install customtkinter"); exit()

    database = Database()
    app = App(db=database)
    app.mainloop()