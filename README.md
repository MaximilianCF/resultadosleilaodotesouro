# Dashboard de Resultados de Leilões do Tesouro Nacional

Este projeto é um **dashboard interativo** desenvolvido em Python utilizando o framework **Streamlit**. O objetivo é fornecer uma visualização detalhada e dinâmica dos resultados dos leilões realizados pelo Tesouro Nacional.

## 🎯 Funcionalidades

- **_Filtragem Dinâmica_**:
  - Escolha o **ano** desejado para buscar os dados dos leilões.
  - Selecione que tipo de leilão **compra** ou **venda**.
  - Selecione **"Todas"** ou uma **data específica do leilão**.
  - Filtre por **tipo de título** e **vencimento**.
- **_Visualização de Dados_**:
  - Tabela interativa com os resultados dos leilões, incluindo:
    - Data do leilão
    - Títulos ofertados
    - Quantidades, taxas e valores financeiros
- **_Gráficos Interativos_**:
  - Volume ofertado vs. aceito
  - Taxas de corte
  - Volume financeiro aceito
  
## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal do projeto.
- **Streamlit**: Framework para criação de dashboards interativos.
- **Pandas**: Manipulação e análise de dados.
- **Requests**: Consumo de APIs RESTful.
- **Plotly**: Criação dos gráficos.

## 🚀 Como Executar

1. **Clone o Repositório**:
   ~~~ bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
2. **Crie um Ambiente Virtual (opcional, mas recomendado):**
   ~~~bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
3. **Instale as Dependências:**
   ~~~bash
   pip install -r requirements.txt
4. **Execute o Dashboard:**
   ~~~bash
   streamlit run dashboard_tesouro.py
5. **Acesse no Navegador:**

   Geralmente em: http://localhost:8501

## 📊 Exemplos de Uso
Exemplo 1: Visualizando Todos os Leilões de um Ano
Selecione o ano desejado e clique em **Buscar Parâmetros**. Escolha "Todas" as datas e aplique filtros por tipo de leilão, de título ou vencimento.

Exemplo 2: Detalhando um Leilão Específico
Escolha o ano e clique em **Buscar Parâmetros**. Selecione tipo de leilão, data do leilão, tipo de título e  vencimento para ver os resultados detalhados.

**OBS.: Quando escolher TODAS as datas do leilão, TODOS os tipos de título e TODOS os vencimentos, o gráfico da taxa de corte não terá uma visualização adequada. Ainda preciso melhorar isto.**

## 🤝 Contribuições

Contribuições são bem-vindas! Siga os passos abaixo para colaborar:

1. **Faça um fork do projeto.**
2. **Crie uma nova branch:**
   ```bash
   git checkout -b minha-feature
3. **Faça as alterações e comente as mudanças:**
   ```bash
   git commit -m "Minha nova feature"
4. **Envie um pull request**

## 📞 Contato

Se tiver dúvidas ou sugestões, entre em contato:

**Email: maximiliancf.cnpi@icloud.com**

**GitHub: MaximilianCF**
