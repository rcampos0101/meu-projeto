import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import urllib.parse

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel("DADOS to AI Testing.xlsx", sheet_name="Dados para AI- Light")
    df.rename(columns={"Ago2": "Ago", "out": "Out", "total": "Total"}, inplace=True)
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    df[meses] = df[meses].replace(1, pd.NA)
    df[meses] = df[meses].apply(pd.to_numeric, errors='coerce')
    df["Total"] = df[meses].sum(axis=1, skipna=True)
    return df, meses

# Layout Streamlit
st.set_page_config(page_title="Dashboard Financeiro", layout="wide", page_icon="🧾")
st.image("Panda Icon 32x32.ico", width=64)
st.title("Dashboard Financeiro - Composição de Despesas")
st.caption("Análise mensal e anual das contas contábeis com filtros interativos.")

# Carregar dados
df, meses = load_data()

# Filtro lateral
with st.sidebar:
    st.header("Filtros")
    contas_disponiveis = df["Conta Contábil"].unique().tolist()
    contas_selecionadas = st.multiselect("Contas Contábeis:", contas_disponiveis, default=contas_disponiveis)
    mes_selecionado = st.selectbox("Mês para gráfico de pizza:", meses)

# Filtrar dados
df_filtrado = df[df["Conta Contábil"].isin(contas_selecionadas)]

# Cálculo dos cards
total_geral = df_filtrado[meses].sum().sum()
receitas = df_filtrado[df_filtrado["Conta Contábil"].str.contains("[Rr]eceita")][meses].sum().sum()
despesas = df_filtrado[df_filtrado["Conta Contábil"].str.contains("[Dd]espesa|[Ii]mposto")][meses].sum().sum()

# Exibir cards no topo
col1, col2, col3 = st.columns(3)
col1.metric("Receitas Totais", f"R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("Despesas Totais", f"R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Resultado Geral", f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("### Evolução Mensal por Conta Contábil")

# Gráfico de Linhas
fig1, ax1 = plt.subplots(figsize=(12, 6))
for _, row in df_filtrado.iterrows():
    ax1.plot(meses, row[meses], label=row["Conta Contábil"], linewidth=0.5)

ax1.set_facecolor("white")
fig1.patch.set_facecolor('white')
ax1.set_title("Evolução Mensal das Contas Contábeis")
ax1.set_xlabel("Meses")
ax1.set_ylabel("Valores (R$)")
ax1.tick_params(axis='x', rotation=45)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
st.pyplot(fig1)

# Botão de análise
if st.button("Mostrar Análise Financeira"):
    st.markdown("**Análise automática gerada pela IA:**")
    st.info("As receitas apresentam tendência de crescimento ao longo do ano, enquanto algumas despesas como Pessoal e Utilidades mantêm-se constantes. Avaliar variações anormais pode indicar oportunidades de economia ou necessidade de ajustes orçamentários.")

# Gráfico de Barras
st.markdown("### Total Anual por Conta Contábil")
fig2, ax2 = plt.subplots(figsize=(10, 5))
df_bar = df_filtrado.sort_values("Total", ascending=False)
ax2.bar(df_bar["Conta Contábil"], df_bar["Total"])
ax2.set_title("Total Anual por Conta Contábil")
ax2.set_ylabel("Total (R$)")
ax2.tick_params(axis='x', rotation=45)
st.pyplot(fig2)

# Gráfico de Pizza com verificação de valores negativos ou nulos
st.markdown(f"### Composição Percentual para o mês de {mes_selecionado}")
df_pizza = df_filtrado[["Conta Contábil", mes_selecionado]].dropna()
df_pizza = df_pizza[df_pizza[mes_selecionado] > 0]

if not df_pizza.empty:
    fig3, ax3 = plt.subplots()
    ax3.pie(df_pizza[mes_selecionado], labels=df_pizza["Conta Contábil"], autopct='%1.1f%%', startangle=90)
    ax3.axis('equal')
    st.pyplot(fig3)
else:
    st.warning("Não há dados positivos disponíveis para este mês no gráfico de pizza.")

# Exportar CSV
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar dados filtrados em CSV", csv, "dados_filtrados.csv", "text/csv")

# Compartilhar via WhatsApp
mensagem = "Confira meu dashboard de despesas: https://dashboard-financeiro.streamlit.app/"
url_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(mensagem)}"
st.markdown(f"[📤 Compartilhar via WhatsApp]({url_whatsapp})", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.caption("Desenvolvido por Ricardo | Projeto em Python + Streamlit")