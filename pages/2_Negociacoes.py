import streamlit as st
import pandas as pd
import sqlite3

def main():
    st.title('Negociações')
    st.divider()
    
    try:
      conn = sqlite3.connect('database.db')
      df = pd.read_sql('SELECT * FROM negociacoes', conn)
      conn.close()
      st.write(df)
    except:
      st.warning('Importe os produtos para visualizar as negociações')


if  __name__ == '__main__':
  main()
    

    