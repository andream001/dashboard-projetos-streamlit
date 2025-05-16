# Importar bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard de Projetos", layout="wide", initial_sidebar_state="expanded")

# --- Carregamento de Dados ---
@st.cache_data # Usar cache para otimizar o carregamento
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Converter colunas de data para datetime
            date_columns = ["DataInicio", "DataFimPrevista", "DataFimReal"]
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo de dados: {e}")
            return None
    return None

# Caminho para o arquivo de dados
DATA_FILE_PATH = "data/project_data.csv"
df_tasks = load_data(DATA_FILE_PATH)

if df_tasks is None:
    st.error(f"Arquivo de dados '{DATA_FILE_PATH}' não encontrado ou erro ao carregar. Verifique se o arquivo existe no local correto e está formatado corretamente.")
    st.stop()

# --- Barra Lateral para Filtros ---
st.sidebar.header("Filtros")

status_options = df_tasks["Status"].unique()
status_filter = st.sidebar.multiselect(
    "Filtrar por Status:",
    options=status_options,
    default=status_options
)

responsavel_options = df_tasks["Responsavel"].unique()
responsavel_filter = st.sidebar.multiselect(
    "Filtrar por Responsável:",
    options=responsavel_options,
    default=responsavel_options
)

prioridade_options = df_tasks["Prioridade"].unique()
prioridade_filter = st.sidebar.multiselect(
    "Filtrar por Prioridade:",
    options=prioridade_options,
    default=prioridade_options
)

# Aplicar filtros
df_filtered = df_tasks[
    df_tasks["Status"].isin(status_filter) &
    df_tasks["Responsavel"].isin(responsavel_filter) &
    df_tasks["Prioridade"].isin(prioridade_filter)
]

if df_filtered.empty:
    st.warning("Nenhuma tarefa encontrada com os filtros aplicados.")
    # Não usar st.stop() aqui para permitir que o título e a estrutura da página ainda sejam exibidos
else:
    # --- Layout Principal ---
    st.title("📊 Dashboard Interativo de Gerenciamento de Projetos")
    st.markdown("## Visão Geral e KPIs")

    # --- KPIs ---
    total_tarefas = df_filtered.shape[0]
    tarefas_concluidas = df_filtered[df_filtered["Status"] == "Concluído"].shape[0]
    percentual_concluidas = (tarefas_concluidas / total_tarefas) * 100 if total_tarefas > 0 else 0
    
    # Considerar tarefas atrasadas como aquelas 'Em Andamento' ou 'Pendente' cuja 'DataFimPrevista' já passou e não há 'DataFimReal'
    tarefas_atrasadas = df_filtered[
        (df_filtered['Status'].isin(['Em Andamento', 'Pendente'])) &
        (df_filtered['DataFimPrevista'] < pd.Timestamp('now', tz='UTC').tz_localize(None)) &
        (df_filtered['DataFimReal'].isnull())
    ].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Tarefas (Filtradas)", total_tarefas)
    col2.metric("Tarefas Concluídas", f"{tarefas_concluidas} ({percentual_concluidas:.2f}%)")
    col3.metric("Tarefas Atrasadas", tarefas_atrasadas)

    st.markdown("--- ")
    st.markdown("## Visualizações Detalhadas")

    # --- Gráficos ---
    # Gráfico 1: Distribuição de Tarefas por Status
    if not df_filtered.empty:
        fig_status = px.pie(df_filtered, names='Status', title='Distribuição de Tarefas por Status', hole=.3)
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
    else:
        fig_status = None
    
    # Gráfico 2: Tarefas por Responsável
    if not df_filtered.empty:
        count_responsavel = df_filtered.groupby('Responsavel').size().reset_index(name='count')
        fig_responsavel = px.bar(count_responsavel, 
                                 x='Responsavel', y='count', title='Número de Tarefas por Responsável', text_auto=True)
    else:
        fig_responsavel = None

    # Gráfico 3: Cronograma de Tarefas (Gantt Simplificado)
    df_gantt = df_filtered.dropna(subset=['DataInicio', 'DataFimPrevista']).copy()
    if not df_gantt.empty:
        # Certificar que DataFimPrevista é sempre maior ou igual a DataInicio para o Gantt
        df_gantt = df_gantt[df_gantt['DataFimPrevista'] >= df_gantt['DataInicio']]
        if not df_gantt.empty:
            fig_gantt = px.timeline(df_gantt, x_start="DataInicio", x_end="DataFimPrevista", y="Descricao", color="Responsavel",
                                    title="Cronograma de Tarefas (Gantt Simplificado)",
                                    labels={"Descricao": "Tarefa"})
            fig_gantt.update_yaxes(categoryorder="total ascending") # Ordenar tarefas
        else:
            fig_gantt = None # Não há dados válidos para o Gantt após o filtro de datas
    else:
        fig_gantt = None # Não há dados para o Gantt

    # Exibir gráficos
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        if fig_status:
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Sem dados para exibir o gráfico de Status.")
            
    with col_graf2:
        if fig_responsavel:
            st.plotly_chart(fig_responsavel, use_container_width=True)
        else:
            st.info("Sem dados para exibir o gráfico de Tarefas por Responsável.")
    
    if fig_gantt:
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("Não há dados suficientes ou válidos para exibir o cronograma (Gantt).")

    # --- Tabela de Dados Detalhada ---
    st.markdown("--- ")
    st.markdown("## Detalhes das Tarefas (Filtradas)")
    st.dataframe(df_filtered)

st.sidebar.markdown("--- ")
st.sidebar.info("Dashboard desenvolvido por Manus AI.")

