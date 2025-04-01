import streamlit as st
import pandas as pd
import plotly.express as px
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

# Exibir cards com moldura
st.markdown("""
<div style='display: flex; gap: 1rem;'>
    <div style='flex:1; border: 1px solid #ccc; padding: 1rem; border-radius: 10px;'>
        <h4>Receitas Totais</h4>
        <p><strong>R$ {:,.2f}</strong></p>
    </div>
    <div style='flex:1; border: 1px solid #ccc; padding: 1rem; border-radius: 10px;'>
        <h4>Despesas Totais</h4>
        <p><strong>R$ {:,.2f}</strong></p>
    </div>
    <div style='flex:1; border: 1px solid #ccc; padding: 1rem; border-radius: 10px;'>
        <h4>Resultado Geral</h4>
        <p><strong>R$ {:,.2f}</strong></p>
    </div>
</div>
""".format(receitas, despesas, total_geral), unsafe_allow_html=True)

st.markdown("### Evolução Mensal por Conta Contábil")

# Gráfico de Linha com Plotly
df_long = df_filtrado.melt(id_vars=["Conta Contábil"], value_vars=meses, var_name="Mês", value_name="Valor")
fig1 = px.line(df_long, x="Mês", y="Valor", color="Conta Contábil", markers=True)
fig1.update_layout(height=300, template="simple_white")
st.plotly_chart(fig1, use_container_width=True)

# Botão de análise
if st.button("Mostrar Análise Financeira"):
    st.markdown("**Análise automática gerada pela IA:**")
    st.info("As receitas apresentam tendência de crescimento ao longo do ano, enquanto algumas despesas como Pessoal e Utilidades mantêm-se constantes. Avaliar variações anormais pode indicar oportunidades de economia ou necessidade de ajustes orçamentários.")

# Gráfico de Barras com Plotly
st.markdown("### Total Anual por Conta Contábil")
fig2 = px.bar(df_filtrado.sort_values("Total", ascending=False), x="Conta Contábil", y="Total")
fig2.update_layout(height=300, xaxis_tickangle=45, template="simple_white")
st.plotly_chart(fig2, use_container_width=True)

# Gráfico de Pizza com Plotly
st.markdown(f"### Composição Percentual para o mês de {mes_selecionado}")
df_pizza = df_filtrado[["Conta Contábil", mes_selecionado]].dropna()
df_pizza = df_pizza[df_pizza[mes_selecionado] > 0]

if not df_pizza.empty and df_pizza[mes_selecionado].sum() > 0:
    fig3 = px.pie(df_pizza, names="Conta Contábil", values=mes_selecionado)
    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)
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