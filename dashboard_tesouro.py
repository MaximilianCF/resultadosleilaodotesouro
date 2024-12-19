import requests
import pandas as pd
import streamlit as st
import plotly.express as px

# Função para buscar os dados da API
def fetch_leilao_data(base_url, ano=None):
    try:
        params = {"ano": ano} if ano else {}
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        registros = data.get("registros", [])

        # Selecionar todas as colunas relevantes e formatar a data
        df = pd.DataFrame(registros)[[
            "DATA", "TITULO", "VENCIMENTO", "OFERTA", "QUANTIDADE ACEITA", "TAXA", "FINANCEIRO ACEITO",
            "QUANTIDADE ACEITA SEGUNDA VOLTA", "FINANCEIRO ACEITO SEGUNDA VOLTA",
            "QUANTIDADE BCB", "FINANCEIRO BCB"
        ]]
        df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True).dt.strftime('%d-%m-%Y')
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

# URL da API
API_URL = "https://apiapex.tesouro.gov.br/aria/v1/api-leiloes-pub/custom/resultados"

# Streamlit Dashboard
st.title("Dashboard de Resultados de Leilões do Tesouro Nacional")
st.write("Visualize dados detalhados de oferta, quantidade aceita e volumes financeiros.")

# Painel lateral com filtros
st.sidebar.header("Filtros de Dados")

# Filtro por ano
ano = st.sidebar.text_input("Ano desejado (ex: 2023):")

# Inicialização de variáveis
data = pd.DataFrame()  # Garante que `data` seja inicializada como um DataFrame vazio
datas_disponiveis = []
vencimentos_disponiveis = []
titulos_disponiveis = []

# Carregar os dados ao escolher o ano
if ano:
    data = fetch_leilao_data(API_URL, ano=ano)

    if not data.empty:
        datas_disponiveis = data["DATA"].unique()
    else:
        st.warning("Nenhum dado retornado para o ano selecionado. Verifique os filtros ou a API.")

# Menu suspenso para data do leilão com a opção "TODAS"
data_leilao = st.sidebar.selectbox("Selecione a Data do Leilão:", ["TODAS"] + list(datas_disponiveis) if len(datas_disponiveis) > 0 else ["TODAS"])

# Filtrar os dados com base na seleção de data
data_filtrada = pd.DataFrame()  # Inicializa como vazio
if data_leilao != "TODAS" and not data.empty:
    data_filtrada = data[data["DATA"] == data_leilao]
elif data_leilao == "TODAS" and not data.empty:
    data_filtrada = data

# Filtro dinâmico por tipo de título
if not data_filtrada.empty:
    titulos_disponiveis = data_filtrada["TITULO"].unique()
    titulo_selecionado = st.sidebar.selectbox("Selecione o Tipo de Título:", ["Todos"] + list(titulos_disponiveis))

    # Aplicar o filtro de tipo de título, se necessário
    if titulo_selecionado != "Todos":
        data_filtrada = data_filtrada[data_filtrada["TITULO"] == titulo_selecionado]

    # Filtro dinâmico por vencimento
    vencimentos_disponiveis = data_filtrada["VENCIMENTO"].unique()
    vencimento = st.sidebar.selectbox("Selecione o Vencimento:", ["Todos"] + list(vencimentos_disponiveis))

    # Aplicar o filtro de vencimento, se necessário
    if vencimento != "Todos":
        data_filtrada = data_filtrada[data_filtrada["VENCIMENTO"] == vencimento]

    # Exibir a tabela e gráficos após os filtros serem aplicados
    if not data_filtrada.empty:
        st.success("Dados filtrados com sucesso!")

        # Mostrar tabela formatada
        st.subheader("Dados Filtrados")
        st.dataframe(data_filtrada)

        # Gráfico: Volume Ofertado x Aceito
        st.subheader("Volume Ofertado x Aceito")
        # st.bar_chart(data_filtrada[["OFERTA", "QUANTIDADE ACEITA"]])
        fig = px.bar(
            data_filtrada,
            x="TITULO",
            y=["OFERTA", "QUANTIDADE ACEITA"],
            barmode="group",
            labels={"value": "Quantidade", "variable": "Tipo"},
            title="Volume Ofertado x Aceito por Título"
        )
        st.plotly_chart(fig)

        # Gráfico: Taxa de Corte
        st.subheader("Taxas de Corte")
        st.line_chart(data_filtrada[["TAXA"]])

        # Gráfico: Volume Financeiro Aceito
        st.subheader("Volume Financeiro Aceito")
        st.bar_chart(data_filtrada[["FINANCEIRO ACEITO"]])

        # Gráfico: Segunda Volta
        st.subheader("Segunda Volta - Dealers")
        st.bar_chart(data_filtrada[["QUANTIDADE ACEITA SEGUNDA VOLTA", "FINANCEIRO ACEITO SEGUNDA VOLTA"]])

        # Gráfico: Banco Central
        st.subheader("Banco Central - Quantidade e Volume")
        st.bar_chart(data_filtrada[["QUANTIDADE BCB", "FINANCEIRO BCB"]])
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    st.info("Insira o ano e clique em 'Carregar Dados' para iniciar.")
