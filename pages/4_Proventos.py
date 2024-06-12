import streamlit as st
import time
import pandas as pd
import sqlite3


def main():
    st.set_page_config(
      page_title="Proventos",
      page_icon="📊",
      layout="wide",
    )

    st.title('Proventos')
    
    conn = sqlite3.connect('database.db')
    df = pd.read_sql('SELECT * FROM proventos', conn)
    conn.close()
    st.write(df)
    
if  __name__ == '__main__':
  main()