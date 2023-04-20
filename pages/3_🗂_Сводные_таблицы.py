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

headers_for_pivot = {
    'Направления реализации молодежной политики': '#### Сводная таблица показателей по направлениям '
                                                  'реализации молодежной '
                                                  'политики по регионам РФ',
    'Структуры по работе с молодежью': '#### Сводная таблица показателей по структурам, работающим '
                                       'с молодежью по регионам РФ',
    'Распространение информации о реализации молодежной политики': '#### Сводная таблица показателей распространения '
                                                                   'информации по регионам РФ',
    'Общественные объединения': '#### Сводная таблица показателей по молодежным объединениям по регионам РФ',
    'Общественные объединения на базе образовательных учреждений': '#### Сводная таблица показателей по '
                                                                   'молодежным объединениям на базе образовательных '
                                                                   'организаций по регионам РФ',
    'Молодежные форумы': '#### Сводная таблица показателей по молодежным форумам по регионам РФ',
    'Добровольчество': '#### Сводная таблица показателей по добровольчеству по регионам РФ'
}

columns_of_2nd_feature = {
    'Направления реализации молодежной политики': 'Направление реализации молодежной политики',
    'Структуры по работе с молодежью': 'Структура по работе с молодежью',
    'Общественные объединения': 'Молодежное объединение',
    'Молодежные форумы': 'Вид форума',
}

headers_for_2d_sections = {
    'Направления реализации молодежной политики': "#### Сводная таблица показателей по различным "
                                                  "направлениям реализации "
                                                  "молодежной политики",
    'Структуры по работе с молодежью': "#### Сводная таблица показателей по различным видам структур по работе "
                                       "с молодежью",
    'Общественные объединения': '#### Сводная таблица показателей по различным видам общественных '
                                'объединений',
    "Молодежные форумы": '#### Сводная таблица показателей по различным видам молодежных '
                         'форумов'
}

agg_func_mapper = {
    'Сумма': 'sum',
    'Среднее': 'mean',
    'Максимальное': 'max'
}

fed_okrug_full_names = {
    'СЗФО': 'Северо-Западный Федеральный Округ',
    'ЦФО': 'Центральный Федеральный Округ',
    "ЮФО": "Южный Федеральный Округ",
    "СКФО": "Северо-Кавказский Федеральный Округ",
    "ПФО": "Приволжский Федеральный Округ",
    "УФО": "Уральский Федеральный Округ",
    "СФО": "Сибирский Федеральный Округ",
    "ДФО": "Дальневосточный Федеральный Округ"
}

reverse_fed_okrug_names = {i: v for (v, i) in fed_okrug_full_names.items()}


@st.cache_data
def read_dataframe(section_name):
    return pd.read_parquet(section_to_df[section_name])


if __name__ == "__main__":
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto",
                       menu_items=None)
    st.title("Сводные таблицы")
    # TODO: Добавить описание страницы

    section = st.selectbox("Выберите раздел показателей",
                           options=list(section_to_df.keys()))

    if section in columns_of_2nd_feature.keys():
        st.markdown('---')

        df = read_dataframe(section_name=section)
        st.markdown(headers_for_2d_sections[section])
        fed_okrug_1 = st.selectbox(label='Выберите федеральный округ',
                                   options=['Все округа'] + [fed_okrug_full_names[fo] for fo in df['Округ'].unique()])
        agg_func_option_1 = st.selectbox(label='Выберите функцию агрегации данных',
                                         options=['Сумма', 'Среднее', 'Максимальное'])
        if fed_okrug_1 == 'Все округа':
            pass
        else:
            df = df[df['Округ'] == reverse_fed_okrug_names[fed_okrug_1]].copy()
        st.dataframe(pd.pivot_table(df,
                                    values='Значение',
                                    columns=['Показатель'],
                                    index=[columns_of_2nd_feature[section]],
                                    aggfunc=agg_func_mapper[agg_func_option_1]))

    st.markdown('---')
    df2 = read_dataframe(section_name=section)
    st.markdown(headers_for_pivot[section])
    fed_okrug_2 = st.selectbox(label='Выберите федеральный округ',
                               options=[fed_okrug_full_names[fo] for fo in df2['Округ'].unique()])
    reg_options = [f'Все субъекты {reverse_fed_okrug_names[fed_okrug_2]}']
    reg_options.extend(df2[df2['Округ'] == reverse_fed_okrug_names[fed_okrug_2]]['Регион'].unique().tolist())
    region = st.selectbox(label='Выберите субъект РФ',
                          options=reg_options)

    if region != f'Все субъекты {reverse_fed_okrug_names[fed_okrug_2]}':
        agg_func_option_2 = 'Сумма'
        df2 = df2[df2['Регион'] == region].copy()
    else:
        df2 = df2[df2['Округ'] == reverse_fed_okrug_names[fed_okrug_2]].copy()
        agg_func_option_2 = st.selectbox(label='Выберите функцию агрегации данных',
                                         options=['Сумма', 'Среднее', 'Максимальное'],
                                         key='second')
    index_cols = ['Регион']

    if section in columns_of_2nd_feature.keys():
        show_2d_feature = st.checkbox(label='Показывать детализацию показателей в сводной таблице',
                                      value=False)

        if show_2d_feature:
            index_cols.extend([columns_of_2nd_feature[section]] )

            print(index_cols)

    st.dataframe(pd.pivot_table(df2,
                                values='Значение',
                                columns=['Показатель'],
                                index=index_cols,
                                aggfunc=agg_func_mapper[agg_func_option_2]))
