import streamlit as st
import time
import pandas as pd
import sqlite3


def main():
    st.title('Proventos')
    st.divider()

    conn = sqlite3.connect('database.db')
    df = pd.read_sql('SELECT * FROM proventos', conn)
    conn.close()
    st.write(df)
    
if  __name__ == '__main__':
  main()