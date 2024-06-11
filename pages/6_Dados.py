import streamlit as st
import pandas as pd
import time
import yfinance as yf
import warnings
import os
from unidecode import unidecode
import sqlite3
import numpy as np

def get_cotacoes():

    conn = sqlite3.connect('database.db')
    df = pd.read_sql('SELECT * FROM produtos', conn)
    conn.close()

    # Rest of the code goes here
    df['Produto'] = df['Produto'] + '.SA'
    tickers = df['Produto'].to_list()
    tickers = ' '.join(tickers)
    data = yf.download(tickers, period='1d')['Close']
    data = data.reset_index()
    data = data.melt(id_vars='Date', var_name='Produto', value_name='Cotacao')
    data = data.rename(columns={'Date': 'Data'})
    data['Data'] = data['Data'].dt.strftime('%Y-%m-%d')
    data = data.merge(df, on='Produto')
    data = data[['Data', 'Produto', 'Cotacao']]
    data['Produto'] = data['Produto'].str.replace('.SA', '')
    
    conn = sqlite3.connect('database.db')
    data.to_sql('cotacoes', conn, if_exists='replace', index=False)
    conn.close()

    return "Cotacoes atualizadas com sucesso!"

def main():

    st.subheader('Cotacoes')

    if st.button('Importar dados'):
        with st.spinner('Importando Dados...'):
            st.toast('Importando proventos...')
            progress_bar = st.progress(0)
            produtos = importar_produtos()
            st.toast(produtos, icon='😁')
            progress_bar.progress(50)
            st.toast('Importando proventos...')
            proventos = importar_proventos()
            st.toast(proventos, icon='😁')
            progress_bar.progress(100)
            st.toast("Dados importados com sucesso", icon='😁')
            time.sleep(3)
            progress_bar.empty()
            

    if st.button(' 🔁 Atualizar Cotações'):
        with st.spinner('Atualizando cotacoes...'):
            progress_bar = st.progress(0)
            cotacoes = get_cotacoes()
            progress_bar.progress(100)
            st.toast("Atualizado com sucesso", icon='😁')
            time.sleep(3)
            progress_bar.empty()
            st.rerun()
    
    if st.button('📤 Upload de arquivos'):
        upload_arquivos()

def importar_proventos():
    # Ignore the specific UserWarning
    warnings.filterwarnings(action='ignore', category=UserWarning, message='Workbook contains no default style, apply openpyxl\'s default')


    folder_path = './dados/sheets'
    file_list = os.listdir(folder_path)

    df_proventos = pd.DataFrame()  # Create an empty DataFrame to store the data

    for file_name in file_list:
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            xls = pd.ExcelFile(file_path)
            
            if 'Proventos Recebidos' in xls.sheet_names:
                df = pd.read_excel(xls, 'Proventos Recebidos')
                df_proventos = pd.concat([df_proventos, df], ignore_index=True)
    
    # Apply unidecode to column names
    df_proventos = df_proventos.rename(columns=lambda x: unidecode(x) if isinstance(x, str) else x)

    df_proventos.dropna(inplace=True)

    df_proventos['Produto'] = df_proventos['Produto'].str.split(' -').str[0]

    df_proventos['Pagamento'] = pd.to_datetime(df_proventos['Pagamento'], dayfirst=True).dt.strftime('%Y-%m-%d')

    df_proventos.drop('Instituicao', axis=1, inplace=True)

    df_proventos['Pagamento'] = pd.to_datetime(df_proventos['Pagamento'])
    df_proventos['Tipo de Evento'] = df_proventos['Tipo de Evento'].astype('category')

    df_proventos['Quantidade'] = df_proventos['Quantidade'].astype('string')
    df_proventos['Quantidade'] = df_proventos['Quantidade'].str.replace(',', '.')
    df_proventos['Quantidade'] = df_proventos['Quantidade'].astype('float')
    df_proventos['Valor liquido'] = df_proventos['Valor liquido'].astype('float')
    df_proventos['Preco unitario'] = df_proventos['Valor liquido'] / df_proventos['Quantidade']
    df_proventos.reset_index(drop=True, inplace=True)

    # Connect to the SQLite database
    conn = sqlite3.connect('database.db')

    # Save the DataFrame to the 'proventos' table in the database
    df_proventos.to_sql('proventos', conn, if_exists='replace', index=False)

    # Close the database connection
    conn.close()

    return "Proventos importados com sucesso!"

def importar_produtos():
    # Ignore the specific UserWarning
    warnings.filterwarnings(action='ignore', category=UserWarning, message='Workbook contains no default style, apply openpyxl\'s default')

    aba = 'Negociações'

    folder_path = './dados/sheets/'
    file_list = os.listdir(folder_path)

    df_negociacoes = pd.DataFrame()  # Create an empty DataFrame to store the data

    for file_name in file_list:
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            xls = pd.ExcelFile(file_path)
            
            if aba in xls.sheet_names:
                df = pd.read_excel(xls, aba)
                df_negociacoes = pd.concat([df_negociacoes, df], ignore_index=True)
        
    # Apply unidecode to column names
    df_negociacoes = df_negociacoes.rename(columns=lambda x: unidecode(x) if isinstance(x, str) else x)
    df_negociacoes['Periodo (Inicial)'] = pd.to_datetime(df_negociacoes['Periodo (Inicial)'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df_negociacoes.rename(columns={'Periodo (Inicial)': 'Data', 'Codigo de Negociacao': 'Produto'}, inplace=True)
    df_negociacoes = df_negociacoes.drop(columns=['Periodo (Final)'])
    df_negociacoes.dropna(inplace=True)
    df_negociacoes['Operacao'] = np.where(df_negociacoes['Quantidade (Compra)'] > 0, 'Compra', 'Venda')
    df_negociacoes['Quantidade'] = df_negociacoes['Quantidade (Compra)'].add(df_negociacoes['Quantidade (Venda)'])
    df_negociacoes['Preco'] = df_negociacoes['Preco Medio (Compra)'].add(df_negociacoes['Preco Medio (Venda)'])
    df_negociacoes.drop(columns=['Quantidade (Compra)','Quantidade (Venda)', 'Quantidade (Liquida)', 'Preco Medio (Compra)', 'Preco Medio (Venda)', 'Instituicao'], inplace=True)
    df_negociacoes['Produto'] = df_negociacoes['Produto'].str.rstrip('F')

    mudancas = {'NUBR33' : 'ROXO34', 'FBOK34': 'M1TA34'}

    df_negociacoes['Produto'] = df_negociacoes['Produto'].replace(mudancas)

    # Connect to the SQLite database
    conn = sqlite3.connect('database.db')

    df_negociacoes.to_sql('negociacoes', conn, if_exists='replace', index=False)
    
    classes = pd.read_csv('./classes.csv')

    classes = classes[['Produto', 'Classe']]

    df_produtos = df_negociacoes[['Produto']].drop_duplicates()
    df_produtos = df_produtos.merge(classes, on='Produto', how='left')
    df_produtos.to_sql('produtos', conn, if_exists='replace', index=False)

    return "Negociacoes importadas com sucesso!"

def upload_arquivos():
    st.subheader('Upload de arquivos')
    uploaded_file = st.file_uploader('Escolha o arquivo', type='xlsx')
    upload_button = st.button('Upload')

if  __name__ == '__main__':
  main()