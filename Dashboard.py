import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

def color_negative_red(value):
    color = 'red' if value < 0 else 'lightgreen'
    return f'color: {color}'

def main():

  st.set_page_config(
    page_title="Dashboard de Investimentos",
    page_icon="📊",
    layout="wide",
  )

  st.title('Dashboard')

  conn = sqlite3.connect('database.db')
  proventos = pd.read_sql('SELECT * FROM proventos', conn)
  produtos = pd.read_sql('SELECT * FROM produtos', conn)
  negociacoes = pd.read_sql('SELECT * FROM negociacoes', conn)
  cotacoes = pd.read_sql('SELECT * FROM cotacoes', conn)
  conn.close()

  carteira = negociacoes
  carteira['Valor'] = carteira['Quantidade'] * carteira['Preco']
  carteira = carteira.groupby('Produto').agg({'Quantidade': 'sum','Valor': 'sum'}).reset_index()
  carteira = carteira.merge(produtos, on='Produto', how='left')
  carteira = carteira.merge(cotacoes, on='Produto', how='left')
  carteira['Valor Atual'] = carteira['Quantidade'] * carteira['Cotacao']
  carteira['Lucro'] = carteira['Valor Atual'] - carteira['Valor']
  carteira['Rentabilidade'] = (carteira['Valor Atual'] / carteira['Valor'] - 1) * 100

  classe = carteira.groupby('Classe').agg({'Valor': 'sum', 'Valor Atual': 'sum'}).reset_index()
  classe['Rentabilidade'] = (classe['Valor Atual'] / classe['Valor'] - 1) * 100
  classe['Rentabilidade'] = classe['Rentabilidade'].round(2)
  classe['Lucro'] = classe['Valor Atual'] - classe['Valor']
  classe['Peso'] = (classe['Valor'] / classe['Valor'].sum()) * 100
  classe['Peso'] = classe['Peso'].round(2)

  total_investido = carteira['Valor'].sum()
  total_atual = carteira['Valor Atual'].sum()
  qtde_ativos = carteira['Produto'].count()
  rentabilidade = (total_atual / total_investido - 1) * 100

  c1m, c2m, c3m, c4m = st.columns(4)
  
  c1m.metric('Total Investido', f'R$ {total_investido:.2f}')
  c2m.metric('Total Atual', f'R$ {total_atual:.2f}', f'R$ {(total_atual - total_investido):.2f}')
  c3m.metric('Rentabilidade', f'{rentabilidade:.2f}%')
  c4m.metric('Quantidade de Ativos', qtde_ativos)

  st.subheader('Distribuição de ativos por classe')

  cc1, cc2 = st.columns(2)

  styled_classe = classe.style.format({
          'Lucro': 'R$ {:,.2f}',
          'Rentabilidade': '{:.2f}%',
          'Valor': 'R$ {:,.2f}',
          'Valor Atual': 'R$ {:,.2f}',
          'Peso': '{:.2f}%'
      }).map(color_negative_red, subset=['Rentabilidade', 'Lucro'])

  cc1.dataframe(styled_classe)

  fig = px.pie(classe, values='Peso', names='Classe')
  cc2.plotly_chart(fig)

  st.subheader('Dividendos')

  if st.checkbox('Proventos por ano'):
      proventos['Ano'] = pd.to_datetime(proventos['Pagamento']).dt.year
      proventos['Ano'] = proventos['Ano'].astype(str)
      proventos = proventos.groupby('Ano').agg({'Valor liquido': 'sum'}).reset_index()
      fig = px.bar(proventos, x='Ano', y='Valor liquido', title='Proventos por ano', text='Valor liquido')
      fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
      st.plotly_chart(fig)
  else:
      proventos['Pagamento'] = pd.to_datetime(proventos['Pagamento'])
      proventos['Pagamento'] = proventos['Pagamento'].dt.strftime('%Y-%m')
      proventos = proventos.groupby('Pagamento').agg({'Valor liquido': 'sum'}).reset_index()      
      fig = px.bar(proventos, x='Pagamento', y='Valor liquido', title='Proventos por Ano-Mes', text='Valor liquido')
      fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
      st.plotly_chart(fig)

  col1, col2 = st.columns(2)

  with col1:
      st.subheader('Top 5 Lucro')
      top_5_lucro = carteira.nlargest(5, 'Rentabilidade')
      top_5_lucro = top_5_lucro[['Produto', 'Rentabilidade', 'Lucro']]
      styled_top_5_lucro = top_5_lucro.style.format({
          'Lucro': 'R${:,.2f}',
          'Rentabilidade': '{:.2f}%'
      }).map(color_negative_red, subset=['Rentabilidade', 'Lucro'])
      st.dataframe(styled_top_5_lucro)

  with col2:
      st.subheader('Top 5 Prejuizo')
      top_5_prejuizo = carteira.nsmallest(5, 'Rentabilidade')	
      top_5_prejuizo = top_5_prejuizo[['Produto', 'Rentabilidade', 'Lucro']]
      styled_top_5_prejuizo = top_5_prejuizo.style.format({
          'Lucro': 'R${:,.2f}',
          'Rentabilidade': '{:.2f}%'
      }).map(color_negative_red, subset=['Rentabilidade', 'Lucro'])
      st.dataframe(styled_top_5_prejuizo)

    
if  __name__ == '__main__':
  main()
