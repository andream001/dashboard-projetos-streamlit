# Dashboard Interativo de Gerenciamento de Projetos

Este projeto é um dashboard interativo construído com Streamlit, Pandas e Plotly para visualizar e analisar dados de gerenciamento de projetos.

## Funcionalidades

- Carrega dados de um arquivo CSV (`data/project_data.csv`).
- Exibe KPIs (Indicadores Chave de Performance) como total de tarefas, percentual de tarefas concluídas e número de tarefas atrasadas.
- Apresenta visualizações interativas:
    - Gráfico de pizza da distribuição de tarefas por status.
    - Gráfico de barras do número de tarefas por responsável.
    - Gráfico de Gantt simplificado para o cronograma das tarefas.
- Permite filtrar os dados por status, responsável e prioridade através de uma barra lateral.
- Mostra uma tabela detalhada com as tarefas filtradas.

## Tecnologias Utilizadas

- Python
- Streamlit (para a interface web do dashboard)
- Pandas (para manipulação e análise de dados)
- Plotly (para gráficos interativos)

## Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/andream001/dashboard-projetos-streamlit.git
    cd dashboard-projetos-streamlit
    ```

2.  **Crie um ambiente virtual (recomendado) e instale as dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run app.py
    ```

    O dashboard deverá abrir automaticamente no seu navegador padrão.

## Estrutura do Projeto

```
dashboard-projetos-streamlit/
├── data/
│   └── project_data.csv  # Arquivo CSV com os dados das tarefas
├── app.py                # Código principal da aplicação Streamlit
├── requirements.txt      # Lista de dependências Python
└── README.md             # Este arquivo
```

## Dados de Exemplo (`project_data.csv`)

O arquivo `project_data.csv` deve conter as seguintes colunas (ou similares):

- `ID`: Identificador único da tarefa.
- `Descricao`: Descrição da tarefa.
- `Responsavel`: Pessoa ou equipe responsável pela tarefa.
- `Status`: Status atual da tarefa (ex: Pendente, Em Andamento, Concluído).
- `DataInicio`: Data de início da tarefa (formato: AAAA-MM-DD).
- `DataFimPrevista`: Data de término prevista para a tarefa (formato: AAAA-MM-DD).
- `DataFimReal`: Data de término real da tarefa (formato: AAAA-MM-DD, pode estar vazia).
- `Prioridade`: Nível de prioridade da tarefa (ex: Alta, Média, Baixa).
- `HorasEstimadas`: Horas estimadas para completar a tarefa.
- `HorasReais`: Horas reais gastas na tarefa.

## Contribuições

Sugestões e contribuições são bem-vindas. Sinta-se à vontade para abrir uma issue ou um pull request.

