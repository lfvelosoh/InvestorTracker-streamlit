import streamlit as st
import pandas as pd
import sqlite3
import yfinance as yf
import time


def main():
    
    st.set_page_config(
      page_title="Produtos",
      page_icon="📊",
      layout="wide",
    )

    try:
      conn = sqlite3.connect('database.db')
      classes = pd.read_sql('SELECT * FROM classes', conn)
      conn.close() 
    except:
      classes = pd.DataFrame()

    try:
      conn = sqlite3.connect('database.db')
      produtos = pd.read_sql('SELECT * FROM produtos', conn)
      conn.close()
    except:
      produtos = pd.DataFrame()

    st.title('Produtos')
    

    if produtos.empty:
        st.warning('Importe os produtos primeiro!')
    else:
        if st.button(' 🔁 Atualizar Cotações'):
            with st.spinner('Atualizando cotacoes...'):
                progress_bar = st.progress(0)
                cotacoes = get_cotacoes()
                progress_bar.progress(100)
                st.write(cotacoes)
                st.toast(cotacoes, icon='😁')
                time.sleep(3)
                progress_bar.empty()
                st.rerun()

    # produtos = produtos.drop(columns=['Data Cotacao', 'Data Atualizacao'])
    produtos = produtos[['Produto', 'Nome', 'Classe', 'Cotacao Atual']]
    produtos_table = st.data_editor(produtos, 
            column_config={
              "Classe": st.column_config.SelectboxColumn(
                "Classe",
                help="Classe do ativo",
                width="medium",
                options=classes['classe'].tolist(),
                required=True,
              ),
            }, hide_index=True
            )
    
    if st.button('Salvar alterações'):
        conn = sqlite3.connect('database.db')
        produtos_table.to_sql('produtos', conn, if_exists='replace', index=False)
        conn.close()
        st.toast('Alterações salvas com sucesso!')


def get_names():
    
    conn = sqlite3.connect('database.db')
    produtos = pd.read_sql('SELECT * FROM produtos', conn)
    conn.close()
    
    names = pd.DataFrame()

    for produto in produtos['Produto']:
        ticker = produto + '.SA'
        ticker = yf.Ticker(ticker)
        name = ticker.info.get('longName')
        new_row = pd.DataFrame({'Produto': [produto], 'Nome': [name]})
        names = pd.concat([names, new_row], ignore_index=True)
    return names


def get_cotacoes():

  conn = sqlite3.connect('database.db')
  produtos = pd.read_sql('SELECT * FROM produtos', conn)
  conn.close()

  tickers = produtos['Produto']
  tickers = tickers.to_list()
  tickers = [x + '.SA' for x in tickers]

  data = yf.download(tickers, period='1d')['Close']
  data = data.reset_index()
  data = data.melt(id_vars='Date', var_name='Produto', value_name='Cotacao')
  data = data.rename(columns={'Date': 'Data Cotacao'})
  data['Data Cotacao'] = data['Data Cotacao'].dt.strftime('%Y-%m-%d')
  data['Produto'] = data['Produto'].str.replace('.SA', '')

  # Fazer o merge com base na coluna 'Produto'
  merged = pd.merge(produtos, data, on='Produto', how='left', suffixes=('', '_novo'))

  # Atualizar 'Cotacao Atual' e 'Data Cotacao' no DataFrame 'produtos'
  produtos['Cotacao Atual'] = merged['Cotacao'].combine_first(merged['Cotacao Atual']).astype(float)
  produtos['Data Cotacao'] = merged['Data Cotacao'].combine_first(merged['Data Cotacao'])
  produtos['Data Atualizacao'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

  names = get_names()
  merged2 = pd.merge(produtos, names, on='Produto', how='left', suffixes=('', '_novo'))

  produtos['Nome'] = merged2['Nome'].combine_first(merged2['Nome_novo'])

  conn = sqlite3.connect('database.db')
  produtos.to_sql('produtos', conn, if_exists='replace', index=False)
  conn.close()

  return "Cotacoes atualizadas com sucesso!"


if  __name__ == '__main__':
  main()
