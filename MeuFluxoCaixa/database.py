# database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file="fluxo_caixa.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Cria as tabelas de entradas e saídas se não existirem."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS saidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def adicionar_entrada(self, descricao, valor):
        """Adiciona um novo registro de entrada."""
        self.cursor.execute(
            "INSERT INTO entradas (descricao, valor, data) VALUES (?, ?, ?)",
            (descricao, valor, datetime.now())
        )
        self.conn.commit()

    def adicionar_saida(self, descricao, valor):
        """Adiciona um novo registro de saída."""
        self.cursor.execute(
            "INSERT INTO saidas (descricao, valor, data) VALUES (?, ?, ?)",
            (descricao, valor, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()

    def buscar_entradas(self):
        """Retorna todas as entradas ordenadas pela mais recente."""
        self.cursor.execute("SELECT id, descricao, valor, data FROM entradas ORDER BY data DESC")
        return self.cursor.fetchall()

    def buscar_saidas(self):
        """Retorna todas as saídas ordenadas pela mais recente."""
        self.cursor.execute("SELECT id, descricao, valor, data FROM saidas ORDER BY data DESC")
        return self.cursor.fetchall()

    def calcular_totais(self):
        """Calcula o total de entradas, saídas e o saldo."""
        self.cursor.execute("SELECT SUM(valor) FROM entradas")
        total_entradas = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("SELECT SUM(valor) FROM saidas")
        total_saidas = self.cursor.fetchone()[0] or 0.0

        saldo = total_entradas - total_saidas
        return total_entradas, total_saidas, saldo
        
    def deletar_transacao(self, tabela, id_transacao):
        """Deleta uma transação específica da tabela 'entradas' ou 'saidas'."""
        if tabela not in ['entradas', 'saidas']:
            print("Erro: Tabela inválida")
            return
            
        self.cursor.execute(f"DELETE FROM {tabela} WHERE id = ?", (id_transacao,))
        self.conn.commit()

    def __del__(self):
        """Fecha a conexão com o banco de dados ao final."""
        self.conn.close()