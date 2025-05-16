# Importar bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard de Projetos", layout="wide", initial_sidebar_state="expanded")

# --- Estilo CSS Customizado (Melhoria Estética) ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    .stMetric {
        border: 1px solid #EEEEEE;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stMetric:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    h1, h2 {
        color: #007BFF; /* Azul para títulos */
    }
    .stButton>button {
        border-radius:20px;
        border:1px solid #007BFF;
        background-color:white;
        color:#007BFF;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color:#007BFF;
        color:white;
    }
</style>
""", unsafe_allow_html=True)

# --- Funções Auxiliares ---
@st.cache_data # Usar cache para otimizar o carregamento
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            date_columns = ["DataInicio", "DataFimPrevista", "DataFimReal"]
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo de dados: {e}")
            return None
    st.error(f"Arquivo de dados não encontrado em: {file_path}")
    return None

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Carregamento de Dados ---
DATA_FILE_PATH = "data/project_data.csv"
df_tasks = load_data(DATA_FILE_PATH)

if df_tasks is None:
    st.error(f"Não foi possível carregar os dados do arquivo 
    st.stop()

# --- Barra Lateral para Filtros ---
st.sidebar.header("⚙️ Filtros Aplicados")

status_options = sorted(df_tasks["Status"].unique())
status_filter = st.sidebar.multiselect(
    "Status da Tarefa:",
    options=status_options,
    default=status_options
)

responsavel_options = sorted(df_tasks["Responsavel"].unique())
responsavel_filter = st.sidebar.multiselect(
    "Responsável:",
    options=responsavel_options,
    default=responsavel_options
)

prioridade_options = sorted(df_tasks["Prioridade"].unique(), key=lambda x: ["Crítica", "Alta", "Média", "Baixa"].index(x) if x in ["Crítica", "Alta", "Média", "Baixa"] else 99)
prioridade_filter = st.sidebar.multiselect(
    "Prioridade:",
    options=prioridade_options,
    default=prioridade_options
)

df_filtered = df_tasks[
    df_tasks["Status"].isin(status_filter) &
    df_tasks["Responsavel"].isin(responsavel_filter) &
    df_tasks["Prioridade"].isin(prioridade_filter)
]

# --- Layout Principal ---
st.title("📊 Dashboard Interativo de Gerenciamento de Projetos")

if df_filtered.empty:
    st.warning("Nenhuma tarefa encontrada com os filtros aplicados.")
else:
    st.markdown("## 🗓️ Visão Geral e KPIs")

    total_tarefas = df_filtered.shape[0]
    tarefas_concluidas = df_filtered[df_filtered["Status"] == "Concluído"].shape[0]
    percentual_concluidas = (tarefas_concluidas / total_tarefas) * 100 if total_tarefas > 0 else 0
    
    tarefas_atrasadas = df_filtered[
        (df_filtered["Status"].isin(["Em Andamento", "Pendente"])) &
        (df_filtered["DataFimPrevista"] < pd.Timestamp("now", tz="UTC").tz_localize(None)) &
        (df_filtered["DataFimReal"].isnull())
    ].shape[0]

    # Adicionando KPI de Horas Estimadas vs Reais (se disponível)
    total_horas_estimadas = df_filtered["HorasEstimadas"].sum()
    total_horas_reais = df_filtered["HorasReais"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Tarefas", total_tarefas, help="Número total de tarefas após filtros.")
    col2.metric("Tarefas Concluídas", f"{tarefas_concluidas} ({percentual_concluidas:.1f}%)", help="Percentual de tarefas concluídas.")
    col3.metric("Tarefas Atrasadas", tarefas_atrasadas, help="Tarefas pendentes/em andamento com prazo expirado.")
    col4.metric("Horas Estimadas", f"{total_horas_estimadas:.0f}h", help="Soma das horas estimadas para as tarefas filtradas.")
    # Poderia adicionar um quinto KPI para Horas Reais se quisesse mais um

    st.markdown("--- ")
    st.markdown("## 📈 Visualizações Detalhadas")

    if not df_filtered.empty:
        # Gráfico 1: Distribuição de Tarefas por Status
        fig_status = px.pie(df_filtered, names="Status", title="Distribuição de Tarefas por Status", hole=.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_status.update_traces(textposition='inside', textinfo='percent+label',
                                  hovertemplate="<b>Status:</b> %{label}<br><b>Tarefas:</b> %{value} (%{percent})<extra></extra>")
        
        # Gráfico 2: Tarefas por Responsável
        count_responsavel = df_filtered.groupby("Responsavel", as_index=False).size().rename(columns={'size':'count'})
        fig_responsavel = px.bar(count_responsavel, 
                                 x="Responsavel", y="count", title="Número de Tarefas por Responsável", text_auto=True,
                                 color="Responsavel", color_discrete_sequence=px.colors.qualitative.Set2)
        fig_responsavel.update_traces(hovertemplate="<b>Responsável:</b> %{x}<br><b>Tarefas:</b> %{y}<extra></extra>")

    else:
        fig_status = None
        fig_responsavel = None

    df_gantt = df_filtered.dropna(subset=["DataInicio", "DataFimPrevista"]).copy()
    if not df_gantt.empty:
        df_gantt = df_gantt[df_gantt["DataFimPrevista"] >= df_gantt["DataInicio"]]
        if not df_gantt.empty:
            df_gantt["Duracao (dias)"] = (df_gantt["DataFimPrevista"] - df_gantt["DataInicio"]).dt.days + 1
            fig_gantt = px.timeline(df_gantt, x_start="DataInicio", x_end="DataFimPrevista", y="Descricao", 
                                    color="Responsavel", title="Cronograma de Tarefas (Gantt Simplificado)",
                                    labels={"Descricao": "Tarefa"},
                                    hover_name="Descricao",
                                    custom_data=["Responsavel", "Status", "Prioridade", "Duracao (dias)"])
            fig_gantt.update_traces(hovertemplate=(
                "<b>Tarefa:</b> %{hovertext}<br>"
                "<b>Responsável:</b> %{customdata[0]}<br>"
                "<b>Status:</b> %{customdata[1]}<br>"
                "<b>Prioridade:</b> %{customdata[2]}<br>"
                "<b>Início:</b> %{base|%d/%m/%Y}<br>"
                "<b>Fim Previsto:</b> %{xEnd|%d/%m/%Y}<br>"
                "<b>Duração:</b> %{customdata[3]} dias<extra></extra>"
            ))
            fig_gantt.update_yaxes(categoryorder="total ascending", automargin=True)
            fig_gantt.update_xaxes(type="date")
        else:
            fig_gantt = None
    else:
        fig_gantt = None

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

    st.markdown("--- ")
    st.markdown("## 📋 Detalhes das Tarefas (Filtradas)")
    
    csv_download = convert_df_to_csv(df_filtered)
    st.download_button(
        label="📥 Baixar dados filtrados como CSV",
        data=csv_download,
        file_name="dados_filtrados_projetos.csv",
        mime="text/csv",
        help="Clique para baixar os dados da tabela abaixo em formato CSV."
    )
    st.dataframe(df_filtered.style.format({
        "DataInicio": "{:%d/%m/%Y}", 
        "DataFimPrevista": "{:%d/%m/%Y}", 
        "DataFimReal": "{:%d/%m/%Y}"
    }, na_rep="-"))

st.sidebar.markdown("--- ")
st.sidebar.info("Dashboard desenvolvido com ❤️ por Manus AI para André Bunhak.")

