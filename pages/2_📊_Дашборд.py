import sys
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.append(".")


@st.cache_resource(ttl=100000)
def plot_map(data,
             geodata,
             first_feature,
             second_feature='all',
             map_style='open-street-map',
             colors='Желтый -> Персиковый -> Фиолетовый'):

    colors_mapper = {
        'Зеленый -> Синий': 'GnBu',
        'Белый -> Розовый -> Фиолетовый': 'RdPu',
        'Белый -> Голубой -> Зеленый': 'PuBuGn',
        'Желтый -> Персиковый -> Фиолетовый': 'Sunset'
    }
    color = colors_mapper[colors]

    if second_feature == 'all':
        temp_df = data.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()

        temp_df = temp_df[temp_df['Показатель'] == first_feature].copy()
    else:
        temp_df = data.groupby(['Регион',
                                'Показатель',
                                'Направления реализации государственной молодeжной политики'])\
            .sum(numeric_only=True).reset_index()
        temp_df = temp_df[(temp_df['Показатель'] == first_feature) &
                          (temp_df['Направления реализации '
                                   'государственной молодeжной политики'] == second_feature)].copy()

    fig = go.Figure()

    fig.add_trace(go.Choroplethmapbox(geojson=geodata, z=temp_df["Значение"],
                                      locations=temp_df["Регион"], featureidkey="properties.full_name",
                                      hovertemplate="<b>%{location}</b><br>Значение показателя = %{z}<extra></extra>",
                                      name=first_feature,
                                      marker_opacity=0.9,
                                      marker_line_width=0.25,
                                      colorscale=color))
    fig.update_layout(margin={"r": 0, "t": 60, "l": 0, "b": 0},
                      mapbox_center={"lat": 64, "lon": 93},
                      mapbox_style=map_style,
                      mapbox_zoom=2,
                      width=1000,
                      height=600,
                      title=first_feature)

    return fig


if __name__ == "__main__":
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto",
                       menu_items=None)
    # TODO: Добавить описание этой страницы
    # TODO: Добавить выбор colorpalette, HxW карты
    st.title("Дашборд")
    df = pd.read_parquet('data/p1.parquet')
    with open('data/geodata.geojson', 'r') as f:
        geojson = json.load(f)

    with st.sidebar:
        # st.write('Параметры карты')
        with st.expander('Параметры карты'):
            mapbox_style = st.radio(
                "Стиль фона карты",
                ('open-street-map', 'carto-positron'),
                help="Выберите каким будет фон карты")
            color_palette = st.radio(
                "Цвета показателей на карте",
                ('Желтый -> Персиковый -> Фиолетовый',
                 'Зеленый -> Синий',
                 'Белый -> Розовый -> Фиолетовый',
                 'Белый -> Голубой -> Зеленый'),
                help="Выберите каким будет фон карты")

    option = st.selectbox(
        'Выберите показатель',
        df['Показатель'].unique().tolist())

    temp_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
    st.plotly_chart(plot_map(data=df,
                             geodata=geojson,
                             first_feature=option,
                             colors=color_palette,
                             map_style=mapbox_style))

    length_of_df_after_option = len(temp_df[temp_df['Показатель'] == option])
    col1, col2, col3 = st.columns([75, 25, 10])
    with col1:
        st.dataframe(temp_df[temp_df['Показатель'] == option],
                     use_container_width=True)
    with col2:
        st.info("Вы можете отсортировать записи в таблице, нажав на поле")


