import streamlit as st
import pandas as pd
import sqlite3

def main():
    st.subheader('Negociações')

    conn = sqlite3.connect('database.db')
    df = pd.read_sql('SELECT * FROM negociacoes', conn)
    conn.close()
    st.write(df)

if  __name__ == '__main__':
  main()
    

    