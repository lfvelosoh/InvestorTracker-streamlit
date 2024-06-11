import streamlit as st
import sqlite3
import pandas as pd

def main():
    conn = sqlite3.connect('database.db')
    produtos = pd.read_sql('SELECT * FROM produtos', conn)
    conn.close()

    st.title('Subscricoes')
    st.write('Aqui estão as subscricoes')

    datafield = st.date_input('Data')
    produto = st.selectbox('Produto', produtos['Produto'])
    quantidade = st.number_input('Quantidade')
    preco = st.number_input('Preco')
    button = st.button('Adicionar')

    if button:
        conn = sqlite3.connect('database.db')
        conn.execute(f"INSERT INTO negociacoes (Data, Produto, Operacao, Quantidade, Preco) VALUES ('{datafield}', '{produto}','Compra' ,{quantidade}, {preco})")
        conn.commit()
        conn.close()
        st.toast('Subscricao adicionada com sucesso')
        
    

if  __name__ == '__main__':
  main()