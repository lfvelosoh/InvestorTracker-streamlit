import streamlit as st
import pandas as pd
from unidecode import unidecode
import sqlite3
import numpy as np
import warnings


warnings.filterwarnings(action='ignore', category=UserWarning, message='Workbook contains no default style, apply openpyxl\'s default')


def processar_produtos():

    try:
        conn = sqlite3.connect('database.db')  # conecta ao banco de dados
        df_produtos = pd.read_sql('SELECT * FROM produtos', conn)  # lê a tabela 'produtos' do banco de dados
        conn.close()  # fecha a conexão com o banco de dados
    except:
        df_produtos = pd.DataFrame()

    try:
        conn = sqlite3.connect('database.db')  # conecta ao banco de dados
        df_negociacoes = pd.read_sql('SELECT * FROM negociacoes', conn)  # lê a tabela 'negociacoes' do banco de dados
        conn.close()  # fecha a conexão com o banco de dados
    except:
        df_negociacoes = pd.DataFrame()

    if df_produtos.empty:
        if not df_negociacoes.empty:
            produtos = df_negociacoes['Produto'].unique()
            produtos = pd.DataFrame(produtos, columns=['Produto'])
            produtos['Classe'] = None
            produtos['Cotacao Atual'] = None
            produtos['Nome'] = None
            produtos['Data Cotacao'] = None
            produtos['Data Atualizacao'] = None
            produtos['OBS'] = None
            conn = sqlite3.connect('database.db')
            produtos.to_sql('produtos', conn, if_exists='replace', index=False)
            conn.close()

    if not df_produtos.empty:
        produtos = df_produtos['Produto'].unique()
        produtos = pd.DataFrame(produtos, columns=['Produto'])
        produtos['Classe'] = None
        produtos['Cotacao Atual'] = None
        produtos['Nome'] = None
        produtos['Data Cotacao'] = None
        produtos['Data Atualizacao'] = None
        produtos['OBS'] = None
        produtos = produtos[~produtos['Produto'].isin(df_produtos['Produto'])]
        conn = sqlite3.connect('database.db')
        produtos.to_sql('produtos', conn, if_exists='append', index=False)
        conn.close()

    return "Produtos importados com sucesso!"


def processar_negociacoes(files, proprietario):
    
    try:        
        conn = sqlite3.connect('database.db')  # conecta ao banco de dados
        negociacoes = pd.read_sql('SELECT * FROM negociacoes', conn)  # lê a tabela 'negociacoes' do banco de dados
        conn.close()  # fecha a conexão com o banco de dados
    except:
        negociacoes = pd.DataFrame()

    df_negociacoes = pd.DataFrame()  # cria um DataFrame vazio

    for file in files:
        
        aba = 'Negociações'
        xls = pd.ExcelFile(file)

        if aba in xls.sheet_names:
            df = pd.read_excel(xls, aba)
            df_negociacoes = pd.concat([df_negociacoes, df], ignore_index=True)

    if not df_negociacoes.empty:
        df_negociacoes = df_negociacoes.rename(columns=lambda x: unidecode(x) if isinstance(x, str) else x)  # aplica unidecode nas colunas
        df_negociacoes.rename(columns={'Periodo (Inicial)': 'Data', 'Codigo de Negociacao': 'Produto'}, inplace=True)  # renomeia as colunas
        df_negociacoes['Data'] = pd.to_datetime(df_negociacoes['Data'], dayfirst=True).dt.strftime('%Y-%m-%d')  # formata a data de negociação
    else:
        return "Negociacoes já importadas!"

    if not negociacoes.empty:
        negociacoes = negociacoes['Data'].unique()  # pega os anos e meses únicos da tabela 'negociacoes'
        negociacoes = pd.to_datetime(negociacoes).strftime('%Y-%m-%d')  # converte os anos e meses para datetime
        df_negociacoes = df_negociacoes[~df_negociacoes['Data'].isin(negociacoes)]  # filtra as negociações que não estão na tabela 'negociacoes'
        
    if not df_negociacoes.empty:    
        df_negociacoes = df_negociacoes.drop(columns=['Periodo (Final)'])  # remove a coluna 'Periodo (Final)'
        df_negociacoes.dropna(inplace=True)  # remove linhas com valores nulos
        df_negociacoes['Operacao'] = np.where(df_negociacoes['Quantidade (Compra)'] > 0, 'Compra', 'Venda')  # cria a coluna 'Operacao'
        df_negociacoes['Quantidade'] = df_negociacoes['Quantidade (Compra)'].add(df_negociacoes['Quantidade (Venda)'])  # calcula a quantidade
        df_negociacoes['Preco'] = df_negociacoes['Preco Medio (Compra)'].add(df_negociacoes['Preco Medio (Venda)'])  # calcula o preço medio
        df_negociacoes.drop(columns=['Quantidade (Compra)','Quantidade (Venda)', 'Quantidade (Liquida)', 'Preco Medio (Compra)', 'Preco Medio (Venda)', 'Instituicao'], inplace=True)  # remove as colunas desnecessárias
        df_negociacoes['Produto'] = df_negociacoes['Produto'].str.rstrip('F')  # remove o 'F' do final do código do produto
        df_negociacoes['Proprietario'] = proprietario  # adiciona o proprietário aos proventos
        df_negociacoes['OBS'] = '-'  # cria a coluna 'OBS'
        df_negociacoes['Data'] = pd.to_datetime(df_negociacoes['Data'])  # converte a coluna 'Data' para datetime
        df_negociacoes['Ano-Mes'] = df_negociacoes['Data'].dt.strftime('%Y-%m')  # cria a coluna 'Ano-Mes' com o ano e mês do pagamento

        mudancas = {'NUBR33' : 'ROXO34', 'FBOK34': 'M1TA34'}  # dicionário com as mudanças de códigos de produtos
        df_negociacoes['Produto'] = df_negociacoes['Produto'].replace(mudancas)  # substitui os códigos de produtos

        conn = sqlite3.connect('database.db')  # conecta ao banco de dados
        df_negociacoes.to_sql('negociacoes', conn, if_exists='append', index=False)  # insere os dados no banco de dados

        return "Negociacoes importadas com sucesso!"


def processar_proventos(files, proprietario):

    try:
        conn = sqlite3.connect('database.db')  # conecta ao banco de dados
        proventos = pd.read_sql('SELECT * FROM proventos', conn)  # lê a tabela 'proventos' do banco de dados
        produtos = pd.read_sql('SELECT * FROM produtos', conn)  # lê a tabela 'produtos' do banco de dados
        conn.close()  # fecha a conexão com o banco de dados
    except:
        proventos = pd.DataFrame()

    df_proventos = pd.DataFrame()  # cria um DataFrame vazio

    for file in files:
        aba = 'Proventos Recebidos'  # nome da aba que contém os proventos
        xls = pd.ExcelFile(file)  # lê o arquivo Excel

        if aba in xls.sheet_names:  # verifica se a aba existe no arquivo Excel
            df = pd.read_excel(xls, aba)  # lê a aba do arquivo Excel
            df_proventos = pd.concat([df_proventos, df], ignore_index=True)  # concatena o DataFrame com os proventos

    if not df_proventos.empty:
        df_proventos = df_proventos.rename(columns=lambda x: unidecode(x) if isinstance(x, str) else x)  # aplica unidecode nas colunas

    if not proventos.empty:
        proventos = proventos['Pagamento'].unique()
        proventos = pd.to_datetime(proventos).strftime('%Y-%m-%d')
        df_proventos = df_proventos[~df_proventos['Pagamento'].isin(proventos)]
    
    if not df_proventos.empty:
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
        df_proventos['Ano-Mes'] = df_proventos['Pagamento'].dt.strftime('%Y-%m')  # cria a coluna 'Ano-Mes' com o ano e mês do pagamento

        conn = sqlite3.connect('database.db')  # conecta ao banco de dados
        df_proventos.to_sql('proventos', conn, if_exists='append', index=False)  # insere os dados no banco de dados
        conn.close()  # fecha a conexão com o banco de dados

        return "Proventos importados com sucesso!"


def main():

    st.set_page_config(
      page_title="Subscricao",
      page_icon="📊",
      #layout="wide",
    )


    st.title('Upload de arquivos')
    

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
                    neg = processar_negociacoes(uploaded_files, proprietario)
                    st.warning(neg)
                    prod = processar_produtos()
                    st.warning(prod)
                    prov = processar_proventos(uploaded_files, proprietario)
                    st.warning(prov)
                
                

if  __name__ == '__main__':
  main()
