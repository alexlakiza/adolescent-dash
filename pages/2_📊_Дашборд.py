import sys
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.append(".")


@st.cache_resource(ttl=100000)
def plot_map(data, geodata, first_feature, second_feature='all'):
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
                                      marker_opacity=0.9, marker_line_width=0.25,
                                      colorscale="GnBu"))
    fig.update_layout(margin={"r": 0, "t": 60, "l": 0, "b": 0},
                      mapbox_center={"lat": 62, "lon": 93},
                      mapbox_style="open-street-map", mapbox_zoom=2,
                      width=900,
                      height=600)

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
        st.write('А как же сайдбар?')

    option = st.selectbox(
        'How would you like to be contacted?',
        df['Показатель'].unique().tolist())

    temp_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
    st.dataframe(temp_df[temp_df['Показатель'] == option])
    st.plotly_chart(plot_map(data=df, geodata=geojson, first_feature=option))
