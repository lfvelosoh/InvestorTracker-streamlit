import streamlit as st
import pandas as pd
from unidecode import unidecode
import sqlite3
import numpy as np
import warnings


warnings.filterwarnings(action='ignore', category=UserWarning, message='Workbook contains no default style, apply openpyxl\'s default')


def processar_negociacoes(files, proprietario):
    for file in files:
        aba = 'Negociações'
        df_negociacoes = pd.DataFrame()
        xls = pd.ExcelFile(file)

        if aba in xls.sheet_names:
            df = pd.read_excel(xls, aba)
            df_negociacoes = pd.concat([df_negociacoes, df], ignore_index=True)
        else:
            pass
    
    df_negociacoes = df_negociacoes.rename(columns=lambda x: unidecode(x) if isinstance(x, str) else x)  # aplica unidecode nas colunas
    df_negociacoes['Periodo (Inicial)'] = pd.to_datetime(df_negociacoes['Periodo (Inicial)'], dayfirst=True).dt.strftime('%Y-%m-%d')  # formata a data de negociação
    df_negociacoes.rename(columns={'Periodo (Inicial)': 'Data', 'Codigo de Negociacao': 'Produto'}, inplace=True)  # renomeia as colunas
    df_negociacoes = df_negociacoes.drop(columns=['Periodo (Final)'])  # remove a coluna 'Periodo (Final)'
    df_negociacoes.dropna(inplace=True)  # remove linhas com valores nulos
    df_negociacoes['Operacao'] = np.where(df_negociacoes['Quantidade (Compra)'] > 0, 'Compra', 'Venda')  # cria a coluna 'Operacao'
    df_negociacoes['Quantidade'] = df_negociacoes['Quantidade (Compra)'].add(df_negociacoes['Quantidade (Venda)'])  # calcula a quantidade
    df_negociacoes['Preco'] = df_negociacoes['Preco Medio (Compra)'].add(df_negociacoes['Preco Medio (Venda)'])  # calcula o preço medio
    df_negociacoes.drop(columns=['Quantidade (Compra)','Quantidade (Venda)', 'Quantidade (Liquida)', 'Preco Medio (Compra)', 'Preco Medio (Venda)', 'Instituicao'], inplace=True)  # remove as colunas desnecessárias
    df_negociacoes['Produto'] = df_negociacoes['Produto'].str.rstrip('F')  # remove o 'F' do final do código do produto
    df_negociacoes['Proprietario'] = proprietario  # adiciona o proprietário aos proventos
    df_negociacoes['OBS'] = '-'  # cria a coluna 'OBS'

    mudancas = {'NUBR33' : 'ROXO34', 'FBOK34': 'M1TA34'}  # dicionário com as mudanças de códigos de produtos
    df_negociacoes['Produto'] = df_negociacoes['Produto'].replace(mudancas)  # substitui os códigos de produtos

    conn = sqlite3.connect('database.db')  # conecta ao banco de dados
    df_negociacoes.to_sql('negociacoes', conn, if_exists='replace', index=False)  # insere os dados no banco de dados

    df_produtos = df_negociacoes[['Produto']].drop_duplicates()  # cria um DataFrame com os produtos
    df_produtos['Classe'] = None  # cria a coluna 'Classe'
    df_produtos['Cotacao Atual'] = None  # cria a coluna 'Cotacao Atual'
    df_produtos['Nome'] = None  # cria a coluna 'Nome'
    df_produtos['Data Cotacao'] = None  # cria a coluna 'Data Cotacao
    df_produtos['Data Atualizacao'] = None  # cria a coluna 'Data Atualizacao'
    df_produtos.to_sql('produtos', conn, if_exists='replace', index=False)  # insere os dados no banco de dados

    return "Negociacoes importadas com sucesso!"


def processar_proventos(files, proprietario):
    for file in files:
        aba = 'Proventos Recebidos'  # nome da aba que contém os proventos
        df_proventos = pd.DataFrame()  # cria um DataFrame vazio
        xls = pd.ExcelFile(file)  # lê o arquivo Excel

        if aba in xls.sheet_names:  # verifica se a aba existe no arquivo Excel
            df = pd.read_excel(xls, aba)  # lê a aba do arquivo Excel
            df_proventos = pd.concat([df_proventos, df], ignore_index=True)  # concatena o DataFrame com os proventos
        else:
            pass

    df_proventos = df_proventos.rename(columns=lambda x: unidecode(x) if isinstance(x, str) else x)  # aplica unidecode nas colunas
    df_proventos.dropna(inplace=True)  # remove linhas com valores nulos
    df_proventos['Produto'] = df_proventos['Produto'].str.split(' -').str[0]  # separa o código do produto
    df_proventos['Pagamento'] = pd.to_datetime(df_proventos['Pagamento'], dayfirst=True).dt.strftime('%Y-%m-%d')  # formata a data de pagamento
    df_proventos.drop('Instituicao', axis=1, inplace=True)  # remove a coluna 'Instituicao'
    df_proventos['Pagamento'] = pd.to_datetime(df_proventos['Pagamento'])  # converte a coluna 'Pagamento' para datetime
    df_proventos['Tipo de Evento'] = df_proventos['Tipo de Evento'].astype('category')  # converte a coluna 'Tipo de Evento' para categoria

    df_proventos['Quantidade'] = df_proventos['Quantidade'].astype('string')  # converte a coluna 'Quantidade' para string
    df_proventos['Quantidade'] = df_proventos['Quantidade'].str.replace(',', '.')  # substitui ',' por '.' na coluna 'Quantidade'
    df_proventos['Quantidade'] = df_proventos['Quantidade'].astype('float')  # converte a coluna 'Quantidade' para float

    df_proventos['Valor liquido'] = df_proventos['Valor liquido'].astype('float')  # converte a coluna 'Valor liquido' para float
    df_proventos['Preco unitario'] = df_proventos['Valor liquido'] / df_proventos['Quantidade']  # calcula o preço unitário
    df_proventos.reset_index(drop=True, inplace=True)  # reseta o índice do DataFrame
    df_proventos['Proprietario'] = proprietario  # adiciona o proprietário aos proventos
    df_proventos['OBS'] = '-'  # cria a coluna 'OBS'

    conn = sqlite3.connect('database.db')  # conecta ao banco de dados
    df_proventos.to_sql('proventos', conn, if_exists='replace', index=False)  # insere os dados no banco de dados
    conn.close()  # fecha a conexão com o banco de dados

    return "Proventos importados com sucesso!"


def main():
    st.title('Upload de arquivos')
    st.divider()

    try:
        conn = sqlite3.connect('database.db')
        proprietarios = pd.read_sql('SELECT * FROM proprietarios', conn)
        conn.close()    
    except:
        proprietarios = pd.DataFrame()

    if proprietarios.empty:
        st.warning('Cadastre os proprietários na aba de configurações!')
    else:
        uploaded_files = st.file_uploader('Escolha os arquivos', type='xlsx', accept_multiple_files=True)
        if uploaded_files:
            proprietario = st.selectbox('proprietario', proprietarios['proprietario'])
            if st.button('Upload'):
                with st.spinner('Processando os dados...'):
                    processar_negociacoes(uploaded_files, proprietario)
                    processar_proventos(uploaded_files, proprietario)
                st.info('Dados processados com sucesso!')
                

if  __name__ == '__main__':
  main()
