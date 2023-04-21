import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import numpy as np
sys.path.append(".")


def calculate_boxplot_params(array):
    q1 = np.quantile(array, q=0.25)
    print(q1)
    median = np.median(array)
    q3 = np.quantile(array, q=0.75, method='hazen')
    iqr = q3 - q1

    lower_fence_lower = q1 - 1.5 * iqr
    upper_fence_upper = q3 + 1.5 * iqr

    lower_fence = max(lower_fence_lower, (array[array >= lower_fence_lower]).min())
    upper_fence = min(upper_fence_upper, (array[array <= upper_fence_upper]).max())

    return q1, median, q3, lower_fence, upper_fence


if __name__ == "__main__":
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto",
                       menu_items=None)
    # TODO: Добавить описание этой страницы
    st.title("Дашборд")

    st.markdown("##### Для начала работы необходимо выбрать тот раздел показателей, по котором вы бы "
                "хотели видеть визуализацию данных")

    df = pd.read_parquet('data/p1.parquet')

    temp_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()

    a = temp_df[(temp_df['Показатель'] == 'Кол-во грантов') &
                         (temp_df['Значение'].notna())]['Значение'].ravel()
    print(type(a))

    q1, med, q3, lf, uf = calculate_boxplot_params(a)

    fig = go.Figure()
    fig.add_trace(go.Box(x=temp_df[(temp_df['Показатель'] == 'Кол-во грантов') &
                         (temp_df['Значение'].notna())]['Значение'],
                         q1=[q1],
                         median=[med],
                         lowerfence=[lf],
                         upperfence=[uf],
                         boxpoints="outliers"
                         ))

    # fig2 = px.box(x=temp_df[(temp_df['Показатель'] == 'Бюджет субъекта РФ на мол. политику') &
    #                      (temp_df['Значение'].notna())]['Значение'],)
    # fig.update_traces(q1=[q1],
    #                   median=[med],
    #                   q3=[q3],
    #                   lowerfence=[lf],
    #                   upperfence=[uf]
    #                   )
    st.plotly_chart(fig, use_container_width=True)

    # st.plotly_chart(fig2, use_container_width=True)
    st.text(f"{q3} q3 with higher")


    st.metric(value=np.quantile(temp_df[(temp_df['Показатель'] == 'Бюджет субъекта РФ на мол. политику') &
                         (temp_df['Значение'].notna())]['Значение'].tolist(), q=0.25), label='25')
    st.metric(value=temp_df[(temp_df['Показатель'] == 'Бюджет субъекта РФ на мол. политику') &
                            (temp_df['Значение'].notna())]['Значение'].quantile(q=0.5, interpolation='linear'), label='50')
    st.metric(value=temp_df[(temp_df['Показатель'] == 'Бюджет субъекта РФ на мол. политику') &
                            (temp_df['Значение'].notna())]['Значение'].quantile(q=0.75, interpolation='higher'), label='75')


