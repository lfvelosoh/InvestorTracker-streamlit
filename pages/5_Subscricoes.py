import streamlit as st
import sqlite3
import pandas as pd

def main():
    st.set_page_config(
      page_title="Subscricao",
      page_icon="📊",
      #layout="wide",
    )


    st.title('Subscricoes')


    

    conn = sqlite3.connect('database.db')
    produtos = pd.read_sql('SELECT * FROM produtos', conn)
    proprietarios = pd.read_sql('SELECT * FROM proprietarios', conn)
    conn.close()

    datafield = st.date_input('Data')
    produto = st.selectbox('Produto', produtos['Produto'])
    proprietario = st.selectbox('Proprietario', proprietarios['proprietario'])
    quantidade = st.number_input('Quantidade')
    preco = st.number_input('Preco')
    button = st.button('Adicionar')

    if button:
        conn = sqlite3.connect('database.db')
        conn.execute(f"INSERT INTO negociacoes (Data, Produto, Operacao, Quantidade, Preco, OBS) VALUES ('{datafield}', '{produto}','Compra' ,{quantidade}, {preco}, 'Subscricao')")
        conn.commit()
        conn.close()
        st.toast('Subscricao adicionada com sucesso')
        
    

if  __name__ == '__main__':
  main()