import streamlit as st
import pandas as pd
import sqlite3


def main():
    st.subheader('Produtos')
    
    conn = sqlite3.connect('database.db')
    df = pd.read_sql('SELECT * FROM produtos', conn)
    conn.close()

    st.write(df)

if  __name__ == '__main__':
  main()