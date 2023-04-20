import sys

import pandas as pd
import streamlit as st

sys.path.append(".")

section_to_df = {
    'Направления реализации молодежной политики': 'data/p1.parquet',
    'Структуры по работе с молодежью': 'data/p2.parquet',
    'Распространение информации о реализации молодежной политики': 'data/p3.parquet',
    'Общественные объединения': 'data/p4.parquet',
    'Общественные объединения на базе образовательных учреждений': 'data/p4-2.parquet',
    'Молодежные форумы': 'data/p6.parquet',
    'Добровольчество': 'data/p7-1.parquet'
}


@st.cache_data
def read_dataframe(section_name):
    return pd.read_parquet(section_to_df[section_name])


if __name__ == "__main__":
    st.title("Сводные таблицы")
    # TODO: Добавить описание страницы

    section = st.selectbox("Выберите раздел показателей",
                           options=list(section_to_df.keys()))
    st.markdown('---')

    df = read_dataframe(section_name=section)

    if section == 'Направления реализации молодежной политики':
        st.dataframe(pd.pivot_table(df[df['Округ'] == 'СЗФО'],
                                    values='Значение',
                                    columns=['Показатель'],
                                    index='Регион',
                                    aggfunc='sum',
                                    margins=True,
                                    margins_name='Сумма'))

        st.markdown('---')
        st.dataframe(df[df['Округ'] == 'СЗФО'].groupby(['Показатель', 'Направление реализации молодежной политики']).sum(numeric_only=True))
