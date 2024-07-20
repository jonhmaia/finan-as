from app import app, db
from models import Entry
from datetime import datetime

# Lista de dados para inserir
entries = [
    {
        "date": "2024-01-05",
        "description": "Compra de Equipamentos",
        "amount": 2500.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
    {
        "date": "2024-02-10",
        "description": "Venda de Produtos",
        "amount": 3000.00,
        "category": "Receita",
        "entry_type": "Entrada"
    },
    {
        "date": "2024-03-15",
        "description": "Pagamento de Serviços",
        "amount": 1500.00,
        "category": "Despesas",
        "entry_type": "Saída"
    },
    {
        "date": "2024-04-20",
        "description": "Recebimento de Consultoria",
        "amount": 2000.00,
        "category": "Receita",
        "entry_type": "Entrada"
    },
    {
        "date": "2024-05-25",
        "description": "Compra de Materiais",
        "amount": 1800.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
    {
        "date": "2024-06-30",
        "description": "Aluguel",
        "amount": 1200.00,
        "category": "Despesas",
        "entry_type": "Saída"
    },
    {
        "date": "2024-07-05",
        "description": "Salário",
        "amount": 3000.00,
        "category": "Despesas",
        "entry_type": "Saída"
    },
    {
        "date": "2024-08-10",
        "description": "Venda de Serviços",
        "amount": 4000.00,
        "category": "Receita",
        "entry_type": "Entrada"
    },
    {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
     {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
      {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
       {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
        {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
         {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
          {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
           {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
            {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
             {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
              {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
               {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
                {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
                 {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
                  {
        "date": "2024-09-15",
        "description": "Compra de Software",
        "amount": 2200.00,
        "category": "Investimento",
        "entry_type": "Saída"
    },
    {
        "date": "2024-10-20",
        "description": "Recebimento de Projeto",
        "amount": 3500.00,
        "category": "Receita",
        "entry_type": "Entrada"
    }
]

# Função para converter a string da data em um objeto date
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

# Configurar o contexto da aplicação
with app.app_context():
    # Inserir os dados no banco de dados
    for entry_data in entries:
        entry = Entry(
            date=parse_date(entry_data["date"]),
            description=entry_data["description"],
            amount=entry_data["amount"],
            category=entry_data["category"],
            entry_type=entry_data["entry_type"]
        )
        db.session.add(entry)

    # Commit das transações
    db.session.commit()

print("Dados inseridos com sucesso!")
