import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Definir como wide view
st.set_page_config(layout="wide")

# Função para buscar os dados da API
@st.cache_data
def fetch_leilao_data(base_url, ano=None, tipo=None):
    try:
        params = {"ano": ano, "tipo": tipo} if ano and tipo else {"ano": ano} if ano else {"tipo": tipo} if tipo else {}
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        registros = data.get("registros", [])

        # Selecionar colunas relevantes e formatar a data
        df = pd.DataFrame(registros)[[
            "DATA", "TITULO", "VENCIMENTO", "OFERTA", "QUANTIDADE ACEITA",
            "QUANTIDADE ACEITA SEGUNDA VOLTA", "TAXA", "FINANCEIRO ACEITO",
            "FINANCEIRO ACEITO SEGUNDA VOLTA", "TIPO"
        ]]
        df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True).dt.strftime('%d-%m-%Y')
        # Preencher valores None com zero
        df = df.fillna({"QUANTIDADE ACEITA SEGUNDA VOLTA": 0, "FINANCEIRO ACEITO SEGUNDA VOLTA": 0})
        # Calculando os totais
        df["TOTAL QUANTIDADE ACEITA"] = df["QUANTIDADE ACEITA"] + df["QUANTIDADE ACEITA SEGUNDA VOLTA"]
        df["TOTAL FINANCEIRO ACEITO"] = df["FINANCEIRO ACEITO"] + df["FINANCEIRO ACEITO SEGUNDA VOLTA"]
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

# Função para buscar os parâmetros possíveis da API
def fetch_leilao_parameters(base_url, ano=None):
    try:
        params = {"ano": ano} if ano else {}
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        registros = data.get("registros", [])

        # Obter valores únicos para os filtros
        df = pd.DataFrame(registros)
        datas_disponiveis = df["DATA"].unique()
        tipos_disponiveis = df["TIPO"].unique()
        titulos_disponiveis = df["TITULO"].unique()
        vencimentos_disponiveis = df["VENCIMENTO"].unique()

        return datas_disponiveis, tipos_disponiveis, titulos_disponiveis, vencimentos_disponiveis
    except Exception as e:
        st.error(f"Erro ao buscar parâmetros: {e}")
        return [], [], [], []

# URL da API
API_URL = "https://apiapex.tesouro.gov.br/aria/v1/api-leiloes-pub/custom/resultados"

# Streamlit Dashboard
st.title("Dashboard de Resultados de Leilões do Tesouro Nacional")
st.write("Visualize dados detalhados de oferta, quantidade aceita e volumes financeiros.")

# Painel lateral com filtros
with st.sidebar:
    st.header("Filtros de Dados", divider="grey")
    st.info("Insira o ano desejado para pesquisa e clique em **'BUSCAR PARÂMETROS'** para carregar os dados."
            " Após, clicar em **'BUSCAR DADOS'**.", icon=":material/arrow_right:")
    st.info("**CASO NÃO EXISTAM DADOS RETORNADOS, AJUSTE OS PARÂMETROS NOVAMENTE** ", icon=':material/arrow_right:')
    st.info("**A API NÃO RETORNA DADOS DA QUANTIDADE OFERTADA EM SEGUNDA VOLTA. COM ISTO, NOS LEILÕES QUE TIVERAM OFERTA EM SEGUNDA VOLTA O GRÁFICO DE QUANTIDADE OFERTADA VAI SER DIFERENTE EM RELAÇÃO À REAL QUANTIDADE OFERTADA.**", icon=':material/notification_important:')

# Filtro por ano
ano = st.sidebar.text_input("Ano desejado (ex: 2023):")

# Inicialização de variáveis para os parâmetros
datas_disponiveis = []
tipos_disponiveis = ["COMPRA", "VENDA"]
titulos_disponiveis = []
vencimentos_disponiveis = []

# Botão para buscar parâmetros
if st.sidebar.button("Buscar Parâmetros", type="primary"):
    datas_disponiveis, tipos_disponiveis, titulos_disponiveis, vencimentos_disponiveis = fetch_leilao_parameters(API_URL, ano=ano)
    st.session_state['datas_disponiveis'] = datas_disponiveis
    st.session_state['tipos_disponiveis'] = tipos_disponiveis
    st.session_state['titulos_disponiveis'] = titulos_disponiveis
    st.session_state['vencimentos_disponiveis'] = vencimentos_disponiveis

# Carregar os parâmetros do estado da sessão
datas_disponiveis = st.session_state.get('datas_disponiveis', [])
tipos_disponiveis = st.session_state.get('tipos_disponiveis', ["COMPRA", "VENDA"])
titulos_disponiveis = st.session_state.get('titulos_disponiveis', [])
vencimentos_disponiveis = st.session_state.get('vencimentos_disponiveis', [])

# Filtro por tipo de leilão
tipo = st.sidebar.selectbox("Selecione o Tipo de Leilão:", tipos_disponiveis)

# Menu suspenso para data do leilão com a opção "TODAS"
data_leilao = st.sidebar.selectbox("Selecione a Data do Leilão:", ["TODAS"] + list(datas_disponiveis))

# Filtro dinâmico por tipo de título
titulo_selecionado = st.sidebar.selectbox("Selecione o Tipo de Título:", ["Todos"] + list(titulos_disponiveis))

# Filtro dinâmico por vencimento
vencimento = st.sidebar.selectbox("Selecione o Vencimento:", ["Todos"] + list(vencimentos_disponiveis))

# Botão de busca
buscar_dados = st.sidebar.button("Buscar Dados", type="primary")

# Inicialização de variáveis
data = pd.DataFrame()  # Garante que `data` seja inicializada como um DataFrame vazio

if buscar_dados:
    data = fetch_leilao_data(API_URL, ano=ano, tipo=tipo)

    if not data.empty:
        # Aplicar filtro por tipo de leilão
        if tipo:
            data = data[data["TIPO"] == tipo]

        # Aplicar filtro de data do leilão
        if data_leilao != "TODAS":
            # Ajustar o formato da data para garantir a comparação correta
            data_leilao = pd.to_datetime(data_leilao, dayfirst=True).strftime('%d-%m-%Y')
            data = data[data["DATA"] == data_leilao]

        # Aplicar filtro de tipo de título
        if titulo_selecionado != "Todos":
            data = data[data["TITULO"] == titulo_selecionado]

        # Aplicar filtro de vencimento
        if vencimento != "Todos":
            data = data[data["VENCIMENTO"] == vencimento]

        # Remover registros onde tanto TOTAL QUANTIDADE ACEITA quanto TOTAL FINANCEIRO ACEITO são zero
        data = data[(data["TOTAL QUANTIDADE ACEITA"] != 0) | (data["TOTAL FINANCEIRO ACEITO"] != 0)]

        # Formatar valores financeiros
        #data["TOTAL FINANCEIRO ACEITO"] = data["TOTAL FINANCEIRO ACEITO"].map('${:,.2f}'.format)
        #data["OFERTA"] = data["OFERTA"].map('${:,.2f}'.format)

        # Verificação se os dados filtrados estão vazios após a aplicação dos filtros
        if not data.empty:
            st.success("Dados filtrados com sucesso!", icon=":material/thumb_up:")

            # Mostrar tabela formatada
            st.subheader("Dados Filtrados")
            st.data_editor(data, disabled=True, hide_index=True, column_config={
                "DATA": {"width": 150},
                "TITULO": {"width": 150},
                "VENCIMENTO": {"width": 150},
                "OFERTA": {"width": 150},
                "TOTAL QUANTIDADE ACEITA": {"width": 150},
                "TOTAL FINANCEIRO ACEITO": {"width": 150}
            })

            # Gráfico: Volume Ofertado x Aceito
            st.subheader("Volume Ofertado x Aceito")
            fig = px.bar(
                data,
                x="TITULO",
                y=["OFERTA", "TOTAL QUANTIDADE ACEITA"],
                barmode="group",
                labels={"value": "Quantidade", "variable": "Tipo"},
                title="Volume Ofertado x Aceito por Título"
            )
            st.plotly_chart(fig)

            # Gráfico: Taxa de Corte
            st.subheader("Taxas de Corte")
            if "TAXA" in data.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data["VENCIMENTO"],
                    y=data["TAXA"],
                    mode='lines+markers',
                    name='Taxa',
                    line=dict(shape='linear'),
                    marker=dict(size=10)
                ))

                # Adiciona uma linha de tendência, se houver dados suficientes
                #if len(data) > 1:
                #    fig.add_trace(go.Scatter(
                #        x=data["VENCIMENTO"],
                #        y=data["TAXA"],
                #        mode='lines',
                #        name='Tendência',
                #        line=dict(dash='dash')
                #    ))

                fig.update_layout(title="Evolução das Taxas de Corte")
                st.plotly_chart(fig)
            else:
                st.warning("Dados insuficientes para gerar o gráfico de Taxas de Corte.")

            # Gráfico: Volume Financeiro Aceito
            st.subheader("Volume Financeiro Aceito")
            if "TOTAL FINANCEIRO ACEITO" in data.columns:
                fig = px.bar(
                    data,
                    x="TITULO",
                    y="TOTAL FINANCEIRO ACEITO",
                    title="Volume Financeiro Aceito por Título",
                    labels={"TOTAL FINANCEIRO ACEITO": "Milhões de R$", "TITULO": "Título"}
                )

                st.plotly_chart(fig)
            else:
                st.warning("Dados insuficientes para gerar o gráfico de Volume Financeiro Aceito.")
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
