import json
import sys

import pandas as pd
import plotly.graph_objects as go
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

columns_of_2nd_feature = {
    'Направления реализации молодежной политики': 'Направление реализации молодежной политики',
    'Структуры по работе с молодежью': 'Структура по работе с молодежью',
    'Общественные объединения': 'Молодежное объединение',
    'Молодежные форумы': 'Вид форума',
}


# @st.cache_resource
def map(data,
        geodata,
        first_feature,
        second_feature=None,
        column_of_2nd_feature=None,
        map_style='open-street-map',
        colors='Желтый -> Персиковый -> Фиолетовый'):
    colors_mapper = {
        'Зеленый -> Синий': 'GnBu',
        'Белый -> Розовый -> Фиолетовый': 'RdPu',
        'Белый -> Голубой -> Зеленый': 'PuBuGn',
        'Желтый -> Персиковый -> Фиолетовый': 'Sunset'
    }
    color = colors_mapper[colors]

    if second_feature == 'Все' or second_feature is None:
        temp_df = data.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()

        temp_df = temp_df[temp_df['Показатель'] == first_feature].copy()
    else:
        temp_df = data.groupby(['Регион',
                                'Показатель',
                                column_of_2nd_feature]) \
            .sum(numeric_only=True).reset_index()

        temp_df = temp_df[(temp_df['Показатель'] == first_feature) &
                          (temp_df[column_of_2nd_feature] == second_feature)].copy()

    fig = go.Figure()

    fig.add_trace(go.Choroplethmapbox(geojson=geodata, z=temp_df["Значение"],
                                      locations=temp_df["Регион"], featureidkey="properties.full_name",
                                      hovertemplate="<b>%{location}</b><br>Значение показателя = %{z}<extra></extra>",
                                      name=first_feature,
                                      marker_opacity=0.9,
                                      marker_line_width=0.25,
                                      colorscale=color))

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox_center={"lat": 64, "lon": 93},
                      mapbox_style=map_style,
                      mapbox_zoom=2,
                      width=950,
                      height=600)

    return fig


@st.cache_data
def read_dataframe(section_name):
    return pd.read_parquet(section_to_df[section_name])


if __name__ == "__main__":
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto",
                       menu_items=None)
    # TODO: Добавить описание этой страницы
    st.title("Дашборд")

    section = st.selectbox("Выберите раздел показателей",
                           options=list(section_to_df.keys()))
    df = read_dataframe(section_name=section)


    with open('data/geodata.geojson', 'r') as f:
        geojson = json.load(f)

    with st.sidebar:
        # st.write('Параметры карты')
        with st.expander('Стиль карты'):
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

    main_option = st.selectbox(
        'Выберите показатель для визуализации',
        options=df['Показатель'].unique().tolist())

    map_title_slice = f"##### Карта субъектов РФ для показателя \"{main_option}\""
    table_title_slice = f"##### Таблица значений показателя \"{main_option}\""

    if section == 'Направления реализации молодежной политики':  # P1
        column_of_2nd_feature = columns_of_2nd_feature[section]
        second_feature_options = df[column_of_2nd_feature].unique().tolist()
        second_option = st.selectbox(
            label='Выберите направление реализации молодежной политики',
            options=['Все'] + second_feature_options
        )

        if second_option == 'Все':
            second_slice_of_title = " по всем направлениям"
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
            st.dataframe(grouped_df[grouped_df['Показатель'] == main_option])
        else:
            second_slice_of_title = f" по направлению \"_{second_option}_\""
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель', column_of_2nd_feature]).sum(numeric_only=True) \
                .reset_index()
            st.dataframe(grouped_df[(grouped_df['Показатель'] == main_option) &
                                    (grouped_df[column_of_2nd_feature] == second_option)])

    elif section == 'Структуры по работе с молодежью':  # P2
        column_of_2nd_feature = columns_of_2nd_feature[section]
        second_feature_options = df[column_of_2nd_feature].unique().tolist()
        second_option = st.selectbox(
            label='Выберите вид структуры по работе с молодежью',
            options=['Все'] + second_feature_options
        )

        if second_option == 'Все':
            second_slice_of_title = " для всех видов структур"
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
            st.dataframe(grouped_df[grouped_df['Показатель'] == main_option])
        else:
            second_slice_of_title = f" для вида структур \"_{second_option}_\""
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель', column_of_2nd_feature]).sum(numeric_only=True) \
                .reset_index()
            st.dataframe(grouped_df[(grouped_df['Показатель'] == main_option) &
                                    (grouped_df[column_of_2nd_feature] == second_option)])

    elif section == 'Распространение информации о реализации молодежной политики':  # P3
        st.markdown(map_title_slice)
        st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, map_style=mapbox_style,
                            colors=color_palette))

        st.markdown(table_title_slice)
        st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
        st.dataframe(df[df['Показатель'] == main_option])

    elif section == 'Общественные объединения':  # P4
        column_of_2nd_feature = columns_of_2nd_feature[section]
        second_feature_options = df[column_of_2nd_feature].unique().tolist()
        second_option = st.selectbox(
            label='Выберите вид молодежных объединений',
            options=['Все'] + second_feature_options
        )

        if second_option == 'Все':
            second_slice_of_title = " для всех видов общ. объединений"
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
            st.dataframe(grouped_df[grouped_df['Показатель'] == main_option])
        else:
            second_slice_of_title = " по виду объединений \"_{second_option}_\""
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель', column_of_2nd_feature]).sum(numeric_only=True) \
                .reset_index()
            st.dataframe(grouped_df[(grouped_df['Показатель'] == main_option) &
                                    (grouped_df[column_of_2nd_feature] == second_option)])

    elif section == 'Общественные объединения на базе образовательных учреждений':  # P4-2
        st.markdown(map_title_slice)
        st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, map_style=mapbox_style,
                            colors=color_palette))

        st.markdown(table_title_slice)
        st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
        st.dataframe(df[df['Показатель'] == main_option])

    elif section == 'Молодежные форумы':  # P6
        column_of_2nd_feature = columns_of_2nd_feature[section]
        second_feature_options = df[column_of_2nd_feature].unique().tolist()
        second_option = st.selectbox(
            label='Выберите вид форумов',
            options=['Все'] + second_feature_options
        )

        if second_option == 'Все':
            second_slice_of_title = " для всех видов форумов"
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
            st.dataframe(grouped_df[grouped_df['Показатель'] == main_option])
        else:
            second_slice_of_title = f" для вида форумов \"{second_option}\""
            st.markdown(map_title_slice + second_slice_of_title)
            st.plotly_chart(map(data=df, geodata=geojson, first_feature=main_option, second_feature=second_option,
                                column_of_2nd_feature=columns_of_2nd_feature[section], map_style=mapbox_style,
                                colors=color_palette))

            st.markdown(table_title_slice + second_slice_of_title)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
            grouped_df = df.groupby(['Регион', 'Показатель', column_of_2nd_feature]).sum(numeric_only=True) \
                .reset_index()
            st.dataframe(grouped_df[(grouped_df['Показатель'] == main_option) &
                                    (grouped_df[column_of_2nd_feature] == second_option)])

    elif section == 'Добровольчество':
        st.markdown(map_title_slice)
        st.plotly_chart(
            map(data=df, geodata=geojson, first_feature=main_option, map_style=mapbox_style, colors=color_palette))

        st.markdown(table_title_slice)
        st.info("Вы можете отсортировать записи в таблице, нажав на поле, а также увеличивать размеры столбцов")
        st.dataframe(df[df['Показатель'] == main_option])


