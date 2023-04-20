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
def map_chart(data,
              geodata,
              first_feature,
              second_feature=None,
              column_of_second_feature=None,
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
                                column_of_second_feature]) \
            .sum(numeric_only=True).reset_index()

        temp_df = temp_df[(temp_df['Показатель'] == first_feature) &
                          (temp_df[column_of_second_feature] == second_feature)].copy()

    fig = go.Figure()

    fig.add_trace(go.Choroplethmapbox(geojson=geodata, z=temp_df["Значение"],
                                      locations=temp_df["Регион"], featureidkey="properties.full_name",
                                      hovertemplate="<b>%{location}</b><br>Значение показателя = %{z}<extra></extra>",
                                      name=first_feature,
                                      marker_opacity=0.9,
                                      marker_line_width=0.25,
                                      colorscale=color))

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox_center={"lat": 64, "lon": 98},
                      mapbox_style=map_style,
                      mapbox_zoom=2)

    return fig


def bar_plot(data,
             first_feature,
             second_feature=None,
             column_of_second_feature=None,
             legend_text_size=12,
             xaxis_title_slice=None):
    if second_feature == 'Все' or second_feature is None:
        mini_grouped_df = data.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()

        top_regions = mini_grouped_df[mini_grouped_df['Показатель'] ==
                                      first_feature].sort_values(by=['Значение'],
                                                                 ascending=False)[:10]['Регион'].tolist()

        if column_of_second_feature:

            temp_df = data[(data['Показатель'] == first_feature) &
                           (data['Регион'].isin(top_regions))].copy()

            fig = go.Figure()

            for second_feature in temp_df[column_of_second_feature].unique():
                fig.add_trace(go.Bar(
                    x=temp_df[temp_df[column_of_second_feature] == second_feature]['Значение'],
                    y=temp_df[temp_df[column_of_second_feature] == second_feature]['Регион'],
                    orientation='h',
                    name=break_long_string(second_feature),
                    hovertemplate=f"{main_option}<br><b>%{{y}}</b><br>Значение = %{{x}}<extra></extra>"
                ))

            fig.update_layout(barmode='stack',
                              margin={"r": 0, "t": 10, "l": 0, "b": 0},
                              legend=dict(font=dict(size=legend_text_size)))
            fig.update_xaxes(title=first_feature)
            return fig

        else:
            temp_df = mini_grouped_df[(mini_grouped_df['Показатель'] == first_feature) &
                                      (mini_grouped_df['Регион'].isin(top_regions))].copy()

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=temp_df['Значение'],
                y=temp_df['Регион'],
                orientation='h',
                name=first_feature,
                hovertemplate=f"{main_option}<br><b>%{{y}}</b><br>Значение = %{{x}}<extra></extra>"
            ))

            fig.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0},
                              legend=dict(font=dict(size=legend_text_size)))
            fig.update_xaxes(title=first_feature)
            return fig

    else:
        temp_df = data[(data['Показатель'] == first_feature) &
                       (data[column_of_second_feature] ==
                        second_feature)].sort_values(by=['Значение'],
                                                     ascending=False)[:10].copy()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=temp_df['Значение'],
            y=temp_df['Регион'],
            orientation='h',
            name=second_feature,
            hovertemplate=f"{main_option}<br><b>%{{y}}</b><br>Значение = %{{x}}<extra></extra>"
        ))

        fig.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0},
                          legend=dict(font=dict(size=legend_text_size)))
        fig.update_xaxes(title=f"{xaxis_title_slice} = {second_feature}")
        return fig


def section_for_map(data,
                    second_slice_of_title_all=None,
                    second_slice_of_title_specific=None,
                    checkbox_label=None,
                    column_of_second_feature=None,
                    bar_plot_xaxis_slice=None):
    if column_of_second_feature:
        second_feature_options = data[column_of_2nd_feature].unique().tolist()
        second_option = st.selectbox(
            label=checkbox_label,
            options=['Все'] + second_feature_options
        )

        if second_option == 'Все':
            map_header = map_title_slice + " " + second_slice_of_title_all
            table_header = table_title_slice + second_slice_of_title_all

            grouped_df = df.groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
            table_to_show = grouped_df[grouped_df['Показатель'] == main_option]

        else:
            second_slice_of_title = f" {second_slice_of_title_specific} \"_{second_option}_\""
            map_header = map_title_slice + second_slice_of_title
            table_header = table_title_slice + second_slice_of_title

            grouped_df = df.groupby(['Регион', 'Показатель', column_of_2nd_feature]).sum(numeric_only=True) \
                .reset_index()
            table_to_show = grouped_df[(grouped_df['Показатель'] == main_option) &
                                       (grouped_df[column_of_2nd_feature] == second_option)]

        st.markdown(map_header)

        st.plotly_chart(map_chart(data=df,
                                  geodata=geojson,
                                  first_feature=main_option,
                                  second_feature=second_option,
                                  column_of_second_feature=column_of_second_feature,
                                  map_style=mapbox_style,
                                  colors=color_palette),
                        use_container_width=True)

        st.markdown(f"##### Топ 10 регионов по выбранному показателю \"{main_option}\"")
        if second_option == 'Все':
            tab3, tab5 = st.tabs(['Диаграмма без детализации', 'С детализацией'])
            with tab3:
                st.plotly_chart(bar_plot(data=df,
                                         first_feature=main_option,
                                         second_feature=second_option),
                                use_container_width=True)
            with tab5:
                st.plotly_chart(bar_plot(data=df,
                                         first_feature=main_option,
                                         second_feature=second_option,
                                         column_of_second_feature=column_of_2nd_feature,
                                         legend_text_size=9),
                                use_container_width=True)
        else:
            st.plotly_chart(bar_plot(data=df,
                                     first_feature=main_option,
                                     second_feature=second_option,
                                     column_of_second_feature=column_of_2nd_feature,
                                     xaxis_title_slice=bar_plot_xaxis_slice),
                            use_container_width=True)

        show_table = st.checkbox(label='Таблица с данными',
                                 help='Показывать таблицу с данными по выбранному показателю?',
                                 value=False)
        if show_table:
            st.markdown(table_header)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле. Также вы можете увеличить размер "
                    "таблицы, потянув за правый нижний угол")
            st.dataframe(table_to_show)

    else:
        st.markdown(map_title_slice)
        st.plotly_chart(map_chart(data=df, geodata=geojson, first_feature=main_option, map_style=mapbox_style,
                                  colors=color_palette),
                        use_container_width=True)

        st.markdown("##### Топ 10 регионов по выбранному показателю")
        st.plotly_chart(bar_plot(data=df,
                                 first_feature=main_option),
                        use_container_width=True)

        show_table = st.checkbox(label='Таблица с данными',
                                 help='Показывать таблицу с данными по выбранному показателю?',
                                 value=False)
        if show_table:
            st.markdown(table_title_slice)
            st.info("Вы можете отсортировать записи в таблице, нажав на поле. Также вы можете увеличить размер "
                    "таблицы, потянув за правый нижний угол")
            st.dataframe(df[df['Показатель'] == main_option])


def break_long_string(string):
    if len(string) > 55:
        median = int(len(string) / 2)

        for i in range(15):
            if string[median + i] == ' ':
                return string[:median + i] + '<br>' + string[median + i + 1:]
    return string


def pie_plot(data, column_name, legend_text_size=12):
    fig = go.Figure()

    fig.add_trace(go.Pie(labels=data[column_name].apply(break_long_string),
                         values=data['Значение']))

    fig.update_layout(uniformtext_mode='hide', uniformtext_minsize=14,
                      legend=dict(font=dict(size=legend_text_size)),  # e.g. family="Courier"
                      margin={"r": 0, "t": 20, "l": 0, "b": 0})
    fig.update_traces(textposition='inside', textinfo='percent',
                      hovertemplate="<b>%{label}</b><br>Значение = %{value}<br>%{percent}<extra></extra>")

    return fig


def section_for_pie_chart(data, header, column_name):
    st.markdown(header)

    region_for_pie = st.selectbox(label='Выберите регион',
                                  options=data['Регион'].unique().tolist())
    main_feature_for_pie = st.selectbox(label='Выберите показатель',
                                        options=data['Показатель'].unique().tolist())

    temp_df = data[(data['Показатель'] == main_feature_for_pie) &
                   (data['Регион'] == region_for_pie)].copy()

    st.plotly_chart(pie_plot(data=temp_df,
                             column_name=column_name),
                    use_container_width=True)

    show_table = st.checkbox(label='Таблица с данными',
                             help='Показывать таблицу с данными по выбранному показателю?',
                             value=False,
                             key='table_for_pie')

    if show_table:
        st.markdown(f'##### Таблица значений показателя \"{main_feature_for_pie}\"')
        st.info("Вы можете отсортировать записи в таблице, нажав на поле. Также вы можете увеличить размер "
                "таблицы, потянув за правый нижний угол")
        st.dataframe(temp_df.drop(['Округ', 'Показатель'], axis=1))


def section_for_volunteer_pie_chart(data2, data3, header2, header3):
    region_for_pie_volunteer = st.selectbox('Выберите регион',
                                            options=df['Регион'].unique().tolist())

    st.markdown(header2)
    st.plotly_chart(pie_plot(data2[data2['Регион'] == region_for_pie_volunteer],
                             column_name='Показатель',
                             legend_text_size=14),
                    use_container_width=True)

    st.markdown(header3)
    st.plotly_chart(pie_plot(data3[data3['Регион'] == region_for_pie_volunteer],
                             column_name='Показатель'),
                    use_container_width=True)


@st.cache_data
def read_dataframe(section_name):
    return pd.read_parquet(section_to_df[section_name])


if __name__ == "__main__":
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto",
                       menu_items=None)
    # TODO: Добавить описание этой страницы
    st.title("Дашборд")

    st.markdown("##### Для начала работы необходимо выбрать тот раздел показателей, по котором вы бы "
                "хотели видеть визуализацию данных")
    section = st.selectbox("Выберите раздел показателей",
                           options=list(section_to_df.keys()))
    st.markdown('---')

    df = read_dataframe(section_name=section)

    with open('data/geodata.geojson', 'r') as f:
        geojson = json.load(f)

    with st.sidebar:
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
    map_title_slice = f"#### Карта субъектов РФ для показателя \"{main_option}\""
    table_title_slice = f"##### Таблица значений показателя \"{main_option}\""

    if section == 'Направления реализации молодежной политики':  # P1
        column_of_2nd_feature = columns_of_2nd_feature[section]

        section_for_map(data=df,
                        second_slice_of_title_all="по всем направлениям",
                        second_slice_of_title_specific="по направлению",
                        checkbox_label="Выберите направление реализации молодежной политики",
                        column_of_second_feature=column_of_2nd_feature,
                        bar_plot_xaxis_slice='Направление')

        section_for_pie_chart(header=f"#### Распределение значений среди направлений "
                                     f"для показателя \"{column_of_2nd_feature}\"",
                              data=df,
                              column_name=column_of_2nd_feature)

    elif section == 'Структуры по работе с молодежью':  # P2
        column_of_2nd_feature = columns_of_2nd_feature[section]
        section_for_map(data=df,
                        second_slice_of_title_all="для всех видов структур",
                        second_slice_of_title_specific="для вида структур",
                        checkbox_label="Выберите вид структуры по работе с молодежью",
                        column_of_second_feature=column_of_2nd_feature,
                        bar_plot_xaxis_slice='Структура')

        section_for_pie_chart(header=f"#### Распределение значений среди видов структур "
                                     f"для показателя \"{column_of_2nd_feature}\"",
                              data=df,
                              column_name=column_of_2nd_feature)

    elif section == 'Распространение информации о реализации молодежной политики':  # P3
        section_for_map(data=df)

    elif section == 'Общественные объединения':  # P4
        column_of_2nd_feature = columns_of_2nd_feature[section]

        section_for_map(data=df,
                        second_slice_of_title_all="для всех видов общ. объединений",
                        second_slice_of_title_specific="по виду объединений",
                        checkbox_label="Выберите вид молодежных объединений",
                        column_of_second_feature=column_of_2nd_feature,
                        bar_plot_xaxis_slice='Объединение')

        section_for_pie_chart(header=f"#### Распределение значений среди видов объединений "
                                     f"для показателя \"{column_of_2nd_feature}\"",
                              data=df,
                              column_name=column_of_2nd_feature)

    elif section == 'Общественные объединения на базе образовательных учреждений':  # P4-2
        section_for_map(data=df)

    elif section == 'Молодежные форумы':  # P6
        column_of_2nd_feature = columns_of_2nd_feature[section]

        section_for_map(data=df,
                        second_slice_of_title_all="для всех видов форумов",
                        second_slice_of_title_specific="для вида форумов",
                        checkbox_label="Выберите вид молодежных форумов",
                        column_of_second_feature=column_of_2nd_feature,
                        bar_plot_xaxis_slice='Форум')

        section_for_pie_chart(header=f"#### Распределение значений среди видов форумов "
                                     f"для показателя \"{column_of_2nd_feature}\"",
                              data=df,
                              column_name=column_of_2nd_feature)

    elif section == 'Добровольчество':
        section_for_map(data=df)

        df2 = pd.read_parquet('data/p7-2.parquet')
        df3 = pd.read_parquet('data/p7-3.parquet')

        section_for_volunteer_pie_chart(data2=df2,
                                        data3=df3,
                                        header2="##### Распределение возрастных категорий "
                                                "граждан, вовлеченных центрами "
                                                "поддержки добровольчества",
                                        header3='##### Распределение числа '
                                                'граждан, вовлеченных в добровольческую '
                                                'деятельность, по направлениям')
