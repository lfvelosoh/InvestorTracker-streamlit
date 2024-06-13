import streamlit as st
import sqlite3
import pandas as pd


def main():

    st.set_page_config(
        page_title="Subscricao",
        page_icon="📊",
        # layout="wide",
    )

    st.title('Configurações')

    tproprietarios, tclasses, tdiversos = st.tabs(['Proprietários', 'Classes', 'Diversos'])

    try:
        conn = sqlite3.connect('database.db')
        proprietarios = pd.read_sql('SELECT * FROM proprietarios', conn)
        conn.close()
    except:
        proprietarios = pd.DataFrame()

    try:
        conn = sqlite3.connect('database.db')
        classes = pd.read_sql('SELECT * FROM classes', conn)
        conn.close()
    except:
        classes = pd.DataFrame()

    with tproprietarios:
        cp1, cp2 = st.columns(2)
        with cp1:
            if not proprietarios.empty:
                proprietarios['Check'] = False
                prorietarios_item = st.data_editor(proprietarios,
                                                   column_config={'Check': st.column_config.CheckboxColumn(
                                                       'Excluir', width='50px'
                                                   )}, hide_index=True)
        with cp2:
            if st.button('Cadastrar Proprietários'):
                cadastro_proprietario()
            if not proprietarios.empty:
                if st.button('Excluir Proprietários'):
                    proprietarios_delete = pd.DataFrame(prorietarios_item)
                    proprietarios_delete = proprietarios_delete[proprietarios_delete['Check'] is False]
                    proprietarios_delete = proprietarios_delete.drop(columns='Check')
                    conn = sqlite3.connect('database.db')
                    proprietarios_delete.to_sql('proprietarios', conn, if_exists='replace', index=False)
                    conn.close()
                    st.rerun()

    with tclasses:
        cc1, cc2 = st.columns(2)
        with cc1:
            if not classes.empty:
                classes['Check'] = False
                classes_item = st.data_editor(classes,
                                              column_config={'Check': st.column_config.CheckboxColumn(
                                                  'Excluir', width='50px'
                                              )}, hide_index=True)
        with cc2:
            if st.button('Cadastrar Classes'):
                cadastro_classe()
            if not classes.empty:
                if st.button('Excluir Classes'):
                    classes_delete = pd.DataFrame(classes_item)
                    classes_delete = classes_delete[classes_delete['Check'] is False]
                    classes_delete = classes_delete.drop(columns='Check')
                    conn = sqlite3.connect('database.db')
                    classes_delete.to_sql('classes', conn, if_exists='replace', index=False)
                    conn.close()
                    st.rerun()

    with tdiversos:
        st.write('Configurações diversas')
        if st.button('Limpar Banco de Dados'):
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute('DROP TABLE IF EXISTS PRODUTOS')
            cur.execute('DROP TABLE IF EXISTS PROVENTOS')
            conn.commit()
            conn.close()


@st.experimental_dialog("Cadastro de Proprietários")
def cadastro_proprietario():
    proprietario = st.text_input("Nome do proprietário", key="proprietario")
    if st.button("Salvar"):
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS proprietarios (proprietario TEXT)')
        cur.execute('INSERT INTO proprietarios VALUES (?)', (proprietario,))
        conn.commit()
        conn.close()
        st.rerun()


@st.experimental_dialog("Cadastro de Classes")
def cadastro_classe():
    classe = st.text_input("Nome da classe", key="classe")
    if st.button("Salvar"):
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS classes (classe TEXT)')
        cur.execute('INSERT INTO classes VALUES (?)', (classe,))
        conn.commit()
        conn.close()
        st.rerun()


if __name__ == '__main__':
    main()
