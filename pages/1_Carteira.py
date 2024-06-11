import streamlit as st
import pandas as pd
import sqlite3


def main():
    st.subheader('Carteira')

    conn = sqlite3.connect('database.db')
    carteira = pd.read_sql('SELECT * FROM produtos', conn)
    proventos = pd.read_sql('SELECT * FROM proventos', conn)
    cotacoes = pd.read_sql('SELECT * FROM cotacoes', conn)
    negociacoes = pd.read_sql('SELECT * FROM negociacoes', conn)
    conn.close()
    
    negociacoes['Total Pago'] = negociacoes['Quantidade'] * negociacoes['Preco']
    negociacoes = negociacoes.groupby('Produto').agg({'Total Pago': 'sum', 'Quantidade': 'sum'}).reset_index()

    carteira = carteira.merge(negociacoes, on='Produto', how='left')
    carteira = carteira.merge(cotacoes, on='Produto', how='left')

    carteira['Preco medio'] = carteira['Total Pago'] / carteira['Quantidade']
    carteira.drop(columns=['Data'], inplace=True)
    carteira['Total Atual'] = carteira['Quantidade'] * carteira['Cotacao']
    carteira['Lucro'] = carteira['Total Atual'] - carteira['Total Pago']
    carteira['Rentabilidade'] = (carteira['Lucro'] / carteira['Total Pago']) * 100
    
    carteira = carteira[['Produto','Classe',  'Quantidade', 'Preco medio','Cotacao', 'Total Atual', 'Total Pago', 'Lucro', 'Rentabilidade']]

        # Função para aplicar estilo baseado em valores
    def color_negative_red(value):
        color = 'red' if value < 0 else 'lightgreen'
        return f'color: {color}'

    styled_carteira= carteira.style.format({
        'Cotacao': 'R${:,.2f}',
        'Total Pago': 'R${:,.2f}',
        'Preco medio': 'R${:,.2f}',
        'Total Atual': 'R${:,.2f}',
        'Lucro': 'R${:,.2f}',
        'Rentabilidade': '{:.2f}%'
    }).map(color_negative_red, subset=['Rentabilidade', 'Lucro'])

    st.dataframe(styled_carteira)

if  __name__ == '__main__':
  main()
    





    
