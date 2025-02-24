import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------
# CONFIGURAÇÕES INICIAIS E CONSTANTES
# -----------------------------------------------
st.set_page_config(
    page_title="Dashboard de Leilões do Tesouro",
    layout="wide"
)

API_URL = "https://apiapex.tesouro.gov.br/aria/v1/api-leiloes-pub/custom/resultados"


# -----------------------------------------------
# FUNÇÕES DE BUSCA E CACHE
# -----------------------------------------------
@st.cache_data
def fetch_leilao_parameters(base_url, ano=None):
    """
    Retorna listas únicas de DATA, TIPO, TITULO e VENCIMENTO para filtros.
    """
    try:
        params = {"ano": ano} if ano else {}
        response = requests.get(base_url, params=params,verify=False)
        response.raise_for_status()
        data = response.json()
        registros = data.get("registros", [])

        df = pd.DataFrame(registros)
        if df.empty:
            return [], [], [], []

        datas_disponiveis = sorted(df["DATA"].unique())
        tipos_disponiveis = sorted(df["TIPO"].unique())
        titulos_disponiveis = sorted(df["TITULO"].unique())
        vencimentos_disponiveis = sorted(df["VENCIMENTO"].unique())

        return datas_disponiveis, tipos_disponiveis, titulos_disponiveis, vencimentos_disponiveis
    except Exception as e:
        st.error(f"Erro ao buscar parâmetros: {e}")
        return [], [], [], []


@st.cache_data
def fetch_leilao_data(base_url, ano=None, tipo=None):
    """
    Busca os dados da API conforme ano e tipo (COMPRA ou VENDA).
    Retorna um DataFrame já com colunas relevantes e cálculos de totais.
    """
    try:
        params = {"ano": ano, "tipo": tipo} if ano and tipo else \
            {"ano": ano} if ano else \
                {"tipo": tipo} if tipo else {}

        response = requests.get(base_url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        registros = data.get("registros", [])

        if not registros:
            return pd.DataFrame()

        df = pd.DataFrame(registros)[[
            "DATA", "TITULO", "VENCIMENTO", "OFERTA", "QUANTIDADE ACEITA",
            "QUANTIDADE ACEITA SEGUNDA VOLTA", "TAXA", "FINANCEIRO ACEITO",
            "FINANCEIRO ACEITO SEGUNDA VOLTA", "TIPO"
        ]]

        # Ajuste de datas
        df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True).dt.strftime('%d-%m-%Y')

        # Preencher valores None com zero
        df = df.fillna({
            "QUANTIDADE ACEITA SEGUNDA VOLTA": 0,
            "FINANCEIRO ACEITO SEGUNDA VOLTA": 0
        })

        # Calculando os totais
        df["TOTAL QUANTIDADE ACEITA"] = df["QUANTIDADE ACEITA"] + df["QUANTIDADE ACEITA SEGUNDA VOLTA"]
        df["TOTAL FINANCEIRO ACEITO"] = df["FINANCEIRO ACEITO"] + df["FINANCEIRO ACEITO SEGUNDA VOLTA"]

        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()


# -----------------------------------------------
# FUNÇÕES DE INTERFACE
# -----------------------------------------------
def show_filters_sidebar():
    """
    Exibe um formulário no sidebar para escolha de filtros
    e retorna os valores escolhidos.
    """
    with st.sidebar.form("filtros"):
        st.header("Filtros de Dados")
        st.info(
            "Insira o ano desejado e clique em **'Buscar Parâmetros'** para atualizar as opções. "
            "Depois clique em **'Buscar Dados'** para carregar o dataset. "
            "Se não houver registros, ajuste os parâmetros."
        )

        # Input para ano
        ano_input = st.text_input("Ano desejado (ex: 2023):", max_chars=4)
        try:
            ano = int(ano_input) if ano_input else None
        except ValueError:
            st.warning("Por favor, insira apenas números para o ano.")
            ano = None

        # Botão para buscar parâmetros
        buscar_parametros = st.form_submit_button("Buscar Parâmetros", type="primary")

    # Se o usuário clicar em 'Buscar Parâmetros', chama a função de parâmetros
    if buscar_parametros:
        with st.spinner("Buscando parâmetros..."):
            datas_disponiveis, tipos_disponiveis, titulos_disponiveis, vencimentos_disponiveis = fetch_leilao_parameters(
                API_URL, ano=ano)
            st.session_state['datas_disponiveis'] = datas_disponiveis
            st.session_state['tipos_disponiveis'] = tipos_disponiveis if tipos_disponiveis else ["COMPRA", "VENDA"]
            st.session_state['titulos_disponiveis'] = titulos_disponiveis
            st.session_state['vencimentos_disponiveis'] = vencimentos_disponiveis
            st.session_state['ano'] = ano

    # Carrega do session state
    datas_disponiveis = st.session_state.get('datas_disponiveis', [])
    tipos_disponiveis = st.session_state.get('tipos_disponiveis', ["COMPRA", "VENDA"])
    titulos_disponiveis = st.session_state.get('titulos_disponiveis', [])
    vencimentos_disponiveis = st.session_state.get('vencimentos_disponiveis', [])
    ano = st.session_state.get('ano', None)

    # Exibe mais um form para filtros complementares
    with st.sidebar.form("filtros_complementares"):
        tipo = st.selectbox("Selecione o Tipo de Leilão:", tipos_disponiveis)
        data_leilao = st.selectbox("Selecione a Data do Leilão:", ["Todas"] + list(datas_disponiveis))
        titulo_selecionado = st.selectbox("Selecione o Título:", ["Todos"] + list(titulos_disponiveis))
        vencimento = st.selectbox("Selecione o Vencimento:", ["Todos"] + list(vencimentos_disponiveis))

        buscar_dados = st.form_submit_button("Buscar Dados", type="primary")

    return ano, tipo, data_leilao, titulo_selecionado, vencimento, buscar_dados


def load_data(ano, tipo):
    """
    Faz a chamada da API, armazena no session_state e retorna o DataFrame.
    """
    if "dados_brutos" not in st.session_state or st.session_state.get(
            'ano_ultimo_fetch') != ano or st.session_state.get('tipo_ultimo_fetch') != tipo:
        # Só refaz a busca se não existir no session_state
        # ou se for um ano/tipo diferente do último fetch
        with st.spinner("Carregando dados..."):
            data = fetch_leilao_data(API_URL, ano=ano, tipo=tipo)
            st.session_state['dados_brutos'] = data
            st.session_state['ano_ultimo_fetch'] = ano
            st.session_state['tipo_ultimo_fetch'] = tipo
    else:
        data = st.session_state['dados_brutos']

    return data


def filter_data(data, tipo, data_leilao, titulo_selecionado, vencimento):
    """
    Aplica os filtros selecionados no sidebar ao DataFrame.
    """
    if data.empty:
        return data

    # Filtro de tipo
    if tipo:
        data = data[data["TIPO"] == tipo]

    # Filtro de data (ajustar string)
    if data_leilao != "Todas":
        data_leilao = pd.to_datetime(data_leilao, dayfirst=True).strftime('%d-%m-%Y')
        data = data[data["DATA"] == data_leilao]

    # Filtro de título
    if titulo_selecionado != "Todos":
        data = data[data["TITULO"] == titulo_selecionado]

    # Filtro de vencimento
    if vencimento != "Todos":
        data = data[data["VENCIMENTO"] == vencimento]

    # Remover registros "zerados"
    data = data[(data["TOTAL QUANTIDADE ACEITA"] != 0) | (data["TOTAL FINANCEIRO ACEITO"] != 0)]

    return data


def show_data(data):
    """
    Exibe a tabela, gráficos e opções de download.
    """
    if data.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    st.success("Dados filtrados com sucesso!")
    st.subheader("Dados Filtrados")

    # Exemplo de formatação com st.data_editor
    st.data_editor(
        data,
        disabled=True,
        hide_index=True,
        column_config={
            "DATA": {"width": 150, "height": 400},
            "TITULO": {"width": 150, "height": 400},
            "VENCIMENTO": {"width": 150, "height": 400},
            "OFERTA": {"width": 150, "height": 400},
            "TAXA": {"width": 80, "height": 400},
            "TOTAL QUANTIDADE ACEITA": {"width": 150, "height": 400},
            "TOTAL FINANCEIRO ACEITO": {
                "width": 150, "height": 400,
                "type": "numeric",
                # Exemplo de formatação monetária (R$)
                "format": "R${:,.2f}"
            }
        }
    )

    # Botão de download do CSV
    csv_data = data.to_csv(index=False)
    st.download_button(
        label="Baixar dados em CSV",
        data=csv_data,
        file_name="resultado_leiloes.csv",
        mime="text/csv"
    )

    # Abas para diferentes gráficos
    tab1, tab2, tab3 = st.tabs(["Volume Ofertado x Aceito", "Taxas de Corte", "Volume Financeiro Aceito"])

    with tab1:
        st.subheader("Volume Ofertado x Aceito")
        if "OFERTA" in data.columns and "TOTAL QUANTIDADE ACEITA" in data.columns:
            fig = px.bar(
                data,
                x="TITULO",
                y=["OFERTA", "TOTAL QUANTIDADE ACEITA"],
                barmode="group",
                labels={"value": "Quantidade", "variable": "Tipo"},
                title="Volume Ofertado x Aceito por Título"
            )
            st.plotly_chart(fig)
        else:
            st.warning("Dados insuficientes para gerar o gráfico.")

    with tab2:
        st.subheader("Taxas de Corte")
        if "TAXA" in data.columns and not data["TAXA"].isnull().all():
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data["VENCIMENTO"],
                y=data["TAXA"],
                mode='lines+markers',
                name='Taxa',
                line=dict(shape='linear'),
                marker=dict(size=10)
            ))
            fig.update_layout(title="Evolução das Taxas de Corte", xaxis_title="Vencimento", yaxis_title="Taxa (%)")
            st.plotly_chart(fig)
        else:
            st.warning("Dados insuficientes para gerar o gráfico de Taxas de Corte.")

    with tab3:
        st.subheader("Volume Financeiro Aceito")
        if "TOTAL FINANCEIRO ACEITO" in data.columns:
            fig = px.bar(
                data,
                x="TITULO",
                y="TOTAL FINANCEIRO ACEITO",
                title="Volume Financeiro Aceito por Título",
                labels={"TOTAL FINANCEIRO ACEITO": "R$ (Total)", "TITULO": "Título"}
            )
            st.plotly_chart(fig)
        else:
            st.warning("Dados insuficientes para gerar o gráfico de Volume Financeiro Aceito.")


# -----------------------------------------------
# LAYOUT PRINCIPAL (MAIN)
# -----------------------------------------------
def main():
    st.title("Dashboard de Resultados de Leilões do Tesouro Nacional")

    # Info adicional (avisos, disclaimers)
    st.info(
        "**Observação**: A API não retorna a quantidade ofertada em segunda volta. "
        "Isso pode fazer com que o gráfico 'Volume Ofertado' fique diferente da "
        "quantidade real nos leilões que tiveram segunda volta."
    )

    # Exibir filtros e capturar retornos
    ano, tipo, data_leilao, titulo_selecionado, vencimento, buscar_dados = show_filters_sidebar()

    # Se clicou em "Buscar Dados", carrega e processa
    if buscar_dados:
        # 1) Carrega ou obtém do cache
        data_bruta = load_data(ano, tipo)
        # 2) Aplica filtros locais
        data_filtrada = filter_data(data_bruta.copy(), tipo, data_leilao, titulo_selecionado, vencimento)
        # 3) Exibe resultado
        show_data(data_filtrada)


if __name__ == "__main__":
    main()
