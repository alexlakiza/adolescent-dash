import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.append(".")


# Объем финансирования МП
def plot_finance_youth_policy_subject_budget(data):
    fig = go.Figure()
    feature_name = "Объем финансирования молодежной политики из бюджета субъектов Российской Федерации"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#636EFA'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Объем финансирования, руб')

    return fig


def plot_finance_youth_policy_organ_selfrule(data):
    fig = go.Figure()
    feature_name = "Объем финансирования молодежной политики из бюджета органов местного самоуправления"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#EF553B'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Объем финансирования, руб')

    return fig


def plot_all_finance_youth_policy(data):
    fig = go.Figure()
    feature_name = "Объем финансирования молодежной политики"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data["Объем финансирования молодежной политики "
                                    "из бюджета субъектов Российской Федерации"],
                             name="Бюджет<br>субъектов РФ",
                             mode='lines+markers',
                             line={'color': '#636EFA'}))

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data["Объем финансирования молодежной политики "
                                    "из бюджета органов местного самоуправления"],
                             name="Бюджет<br>органов<br>местного<br>самоуправления",
                             mode='lines+markers',
                             line={'color': '#EF553B'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Объем финансирования, руб')

    return fig


# Гранты
def plot_n_grants(data):
    fig = go.Figure()
    feature_name = "Количество грантов, выданных физическим и " \
                   "юридическим лицам, в рамках<br>реализации " \
                   "государственной молодежной политики"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#00CC96'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Количество грантов, ед')

    return fig


def plot_money_grants(data):
    fig = go.Figure()
    feature_name = "Объем грантовых средств, выданных физическим и " \
                   "юридическим лицам, в рамках<br>реализации " \
                   "государственной молодежной политики"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#AB63FA'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Объем грантовых средств, руб')

    return fig


# Общественные объединения
def plot_n_region_unities(data):
    fig = go.Figure()
    feature_name = "Количество региональных общественных объединений, пользующихся государственной поддержкой"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#FFA15A'}))

    fig.update_layout(title="Количество региональных общественных объединений, пользующихся<br>государственной "
                            "поддержкой")
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Кол-во объединений, ед')

    return fig


def plot_n_local_unities(data):
    fig = go.Figure()
    feature_name = "Количество местных общественных объединений, пользующихся поддержкой"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#19D3F3'}))

    fig.update_layout(title="Количество местных общественных объединений, пользующихся<br>государственной поддержкой")
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Кол-во объединений, ед')

    return fig


# Органы молодежного самоуправления
def plot_n_youth_selfrule(data):
    fig = go.Figure()
    feature_name = "Количество органов молодежного самоуправления"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#FF6692'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Кол-во органов, ед')

    return fig


def plot_all_n_unities_organs(data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data["Количество региональных общественных объединений, "
                                    "пользующихся государственной поддержкой"],
                             name="Количество<br>региональных<br>общ. объединений,<br>пользующихся<br>гос. поддержкой",
                             mode='lines+markers',
                             line={'color': '#FFA15A'}))

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data["Количество местных общественных объединений, пользующихся поддержкой"],
                             name="Количество<br>местных<br>общ. объединений,<br>пользующихся<br>гос. поддержкой",
                             mode='lines+markers',
                             line={'color': '#19D3F3'}))

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data["Количество органов молодежного самоуправления"],
                             name="Количество<br>органов<br>молодежного<br>самоуправления",
                             mode='lines+markers',
                             line={'color': '#FF6692'}))

    fig.update_layout(title='Количество общ. объединений, поддерживаемых гос-вом, '
                            'и органов молодежного самоуправления')
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Кол-во органов, ед')

    return fig


# Форумы
def plot_n_forums(data):
    fig = go.Figure()
    feature_name = "Количество молодежных форумов, прошедших на территории субъектов<br>Российской Федерации"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#109618'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Кол-во форумов, ед')

    return fig


def plot_n_people_forums(data):
    fig = go.Figure()
    feature_name = "Численность участников молодежных форумов"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#990099'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Кол-во участников, чел')

    return fig


def plot_finance_forum_subject(data):
    fig = go.Figure()
    feature_name = "Объем финансирования молодежных форумов из средств бюджетов<br>субъектов Российской Федерации"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#636EFA'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Объем финансирования, руб')

    return fig


def plot_finance_forum_local(data):
    fig = go.Figure()
    feature_name = "Объем финансирования молодежных форумов из средств органов бюджетов местного самоуправления"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[feature_name.replace('<br>', ' ')],
                             name=feature_name,
                             mode='lines+markers',
                             line={'color': '#EF553B'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Объем финансирования, руб')

    return fig


def plot_all_finance_forum(data):
    fig = go.Figure()
    feature_name = "Объем финансирования форумов"

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data["Объем финансирования молодежных форумов из средств "
                                    "бюджетов субъектов Российской Федерации"],
                             name="Бюджет<br>субъектов РФ",
                             mode='lines+markers',
                             line={'color': '#636EFA'}))

    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data["Объем финансирования молодежных форумов из средств "
                                    "органов бюджетов местного самоуправления"],
                             name="Бюджет<br>органов<br>местного<br>самоуправления",
                             mode='lines+markers',
                             line={'color': '#EF553B'}))

    fig.update_layout(title=feature_name)
    fig.update_xaxes(title='Год', tickformat="%Y")
    fig.update_yaxes(title='Объем финансирования, руб')

    return fig


if __name__ == "__main__":
    st.title("Статистика по годам")
    # TODO: Добавить описание страницы

    with st.sidebar:
        st.write("Графики на странице:")
        finance_youth_policy = st.checkbox("Объем финансирования молодежной политики",
                                           value=True,
                                           help='Показывать графики объемов финансирования молодежной политики')

        grants = st.checkbox("Количество грантов и объем грантовых средств",
                             value=True,
                             help='Показывать графики грантов')

        unities = st.checkbox("Количество общ. объединений и органов молодежного самоуправления",
                              value=True,
                              help='Показывать графики количества региональных и местных общественных объединений и '
                                   'органов молодежного самоуправления')

        forums = st.checkbox("Количество, численность участников и объем финансирования молодежных форумов",
                             value=True,
                             help='Показывать количество проведенных форумов, численность участников и объем '
                                  'финансирования форумов')

    df = pd.read_parquet('data/p8.parquet')

    if finance_youth_policy:
        st.markdown("#### Графики объемов финансирования молодежной политики")
        tab2, tab1 = st.tabs(["Общий график объемов финансирования", "Графики по отдельности"])
        with tab1:
            st.plotly_chart(plot_finance_youth_policy_subject_budget(df))
            st.plotly_chart(plot_finance_youth_policy_organ_selfrule(df))
        with tab2:
            st.plotly_chart(plot_all_finance_youth_policy(df))

        st.markdown('---')

    if grants:
        st.markdown("#### Графики количества выданных грантов и грантовых средств")
        st.plotly_chart(plot_n_grants(df))
        st.plotly_chart(plot_money_grants(df))

        st.markdown('---')

    if unities:
        st.markdown("#### Графики количества общественных объединений и органов молодежного самоуправления")
        tab1, tab2 = st.tabs(["Общий график", "Графики по отдельности"])
        with tab1:
            st.plotly_chart(plot_all_n_unities_organs(df))
        with tab2:
            st.plotly_chart(plot_n_region_unities(df))
            st.plotly_chart(plot_n_local_unities(df))
            st.plotly_chart(plot_n_youth_selfrule(df))

        st.markdown('---')

    if forums:
        st.markdown("#### Графики количества проведенных форумов, численности участников и объемов "
                    "финансирования форумов")
        st.plotly_chart(plot_n_forums(df))
        st.plotly_chart(plot_n_people_forums(df))
        tab2, tab1 = st.tabs(["Общий график объемов финансирования", "Графики по отдельности"])
        with tab1:
            st.plotly_chart(plot_finance_forum_subject(df))
            st.plotly_chart(plot_finance_forum_local(df))
        with tab2:
            st.plotly_chart(plot_all_finance_forum(df))
