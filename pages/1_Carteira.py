import streamlit as st
import pandas as pd
import sqlite3
from utils.functions import color_negative_red


def main():
    st.title('Carteira')
    st.divider()

    try:
        conn = sqlite3.connect('database.db')
        carteira = pd.read_sql('SELECT * FROM produtos', conn)
        negociacoes = pd.read_sql('SELECT * FROM negociacoes', conn)
        conn.close()
        
        negociacoes['Total Pago'] = negociacoes['Quantidade'] * negociacoes['Preco']
        negociacoes = negociacoes.groupby('Produto').agg({'Total Pago': 'sum', 'Quantidade': 'sum'}).reset_index()

        carteira = carteira.merge(negociacoes, on='Produto', how='left')

        carteira['Preco medio'] = carteira['Total Pago'] / carteira['Quantidade']
        carteira['Total Atual'] = carteira['Quantidade'] * carteira['Cotacao Atual']
        carteira['Lucro'] = carteira['Total Atual'] - carteira['Total Pago']
        carteira['Rentabilidade'] = (carteira['Lucro'] / carteira['Total Pago']) * 100
        
        carteira = carteira[['Produto','Classe',  'Quantidade', 'Preco medio','Cotacao Atual', 'Total Atual', 'Total Pago', 'Lucro', 'Rentabilidade']]

            # Função para aplicar estilo baseado em valores

        styled_carteira= carteira.style.format({
            'Cotacao Atual': 'R${:,.2f}',
            'Total Pago': 'R${:,.2f}',
            'Preco medio': 'R${:,.2f}',
            'Total Atual': 'R${:,.2f}',
            'Lucro': 'R${:,.2f}',
            'Rentabilidade': '{:.2f}%'
        }).map(color_negative_red, subset=['Rentabilidade', 'Lucro'])

        st.dataframe(styled_carteira)
    except:
        st.warning('Importe os produtos e atualize as cotações para visualizar a carteira')

if  __name__ == '__main__':
  main()
    





    
