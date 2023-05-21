import json
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.append(".")

section_to_df = {
    'Направления реализации молодежной политики': 'p1.parquet',
    'Структуры по работе с молодежью': 'p2.parquet',
    'Информационное обеспечение реализации молодежной политики': 'p3.parquet',
    'Общественные объединения': 'p4.parquet',
    'Общественные объединения на базе образовательных учреждений': 'p4-2.parquet',
    'Молодежные форумы': 'p6.parquet',
    'Добровольчество': 'p7-1.parquet'
}

columns_of_2nd_feature = {
    'Направления реализации молодежной политики': 'Направление реализации молодежной политики',
    'Структуры по работе с молодежью': 'Структура по работе с молодежью',
    'Общественные объединения': 'Молодежное объединение',
    'Молодежные форумы': 'Вид форума',
}

years_to_analyze = ['2021', '2020', '2019']


def reformat_string_value(val):
    """ Convert number 8939484 to 8 939 484"""
    try:
        return format(int(val), ',').replace(',', ' ').replace('.', ',')
    except ValueError:
        return '0'


def generate_comparison_for_map_chart(val, prev_year_name):
    if val == 0:
        return f"<br>Значение с {prev_year_name} года<br>не изменилось"
    elif val > 0:
        val = reformat_string_value(val)
        return f"<br>+{val} по сравнению с {prev_year_name} годом"
    else:
        val = reformat_string_value(val)
        return f"<br>{val} по сравнению с {prev_year_name} годом"


def break_long_region_name(test_str):
    if len(test_str.split(' ')) >= 3:
        parts = test_str.split(' ')

        left_parts = parts[:2]
        right_parts = parts[2:]
        return ' '.join(left_parts) + '\n' + ' '.join(right_parts)
    return test_str


def map_chart(data,
              geodata,
              first_feature,
              map_style='open-street-map',
              colors='Желтый -> Персиковый -> Фиолетовый'):
    colors_mapper = {
        'Зеленый -> Синий': 'GnBu',
        'Белый -> Розовый -> Фиолетовый': 'RdPu',
        'Белый -> Голубой -> Зеленый': 'PuBuGn',
        'Желтый -> Персиковый -> Фиолетовый': 'Sunset'
    }
    color = colors_mapper[colors]

    temp_df = data[data['Год'] == chosen_year].copy()
    if chosen_year == '2019':
        custom_data = ['<br>Нет данных, чтобы сравнить значения 2019 и 2018 годов' for _ in range(len(temp_df))]
    else:
        prev_year = str(int(chosen_year) - 1)
        prev_year_df = data[data['Год'] == prev_year].copy()

        custom_data = [generate_comparison_for_map_chart(i,
                                                         prev_year) for i
                       in temp_df['Значение'].values - prev_year_df['Значение'].values]

    custom_text = [reformat_string_value(i) for i in temp_df["Значение"].values]

    fig = go.Figure()
    fig.add_trace(go.Choroplethmapbox(geojson=geodata,
                                      z=temp_df["Значение"],
                                      locations=temp_df["Регион"],
                                      customdata=custom_data,
                                      text=custom_text,
                                      featureidkey="properties.full_name",
                                      hovertemplate="<b>%{location}</b><br>Значение показателя = "
                                                    f"%{{text}} в {chosen_year} году<br>"
                                                    f"%{{customdata}}<extra></extra>",
                                      name=first_feature,
                                      marker={'opacity': 0.9,
                                              'line_width': 0.25},
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
    if column_of_second_feature:
        fig = go.Figure()

        for second_feature in data[column_of_second_feature].unique():
            fig.add_trace(go.Bar(
                x=data[data[column_of_second_feature] == second_feature]['Значение'],
                y=data[data[column_of_second_feature] == second_feature]['Регион'],
                orientation='h',
                name=break_long_string(second_feature),
                hovertemplate=f"{main_option}<br><b>%{{y}}</b><br>Значение = %{{x}}<extra></extra>"
            ))

        fig.update_layout(barmode='stack',
                          margin={"r": 0, "t": 10, "l": 0, "b": 0},
                          legend=dict(font=dict(size=legend_text_size)))
        if second_feature:
            fig.update_xaxes(title=f"{xaxis_title_slice} = {second_feature}")
        else:
            fig.update_xaxes(title=first_feature)
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data['Значение'],
            y=data['Регион'],
            orientation='h',
            name=first_feature,
            hovertemplate=f"{main_option}<br><b>%{{y}}</b><br>Значение = %{{x}}<extra></extra>"
        ))

        fig.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0},
                          legend=dict(font=dict(size=legend_text_size)))
        fig.update_xaxes(title=first_feature)
    return fig


def section_for_map(data,
                    second_slice_of_title_all=None,
                    second_slice_of_title_specific=None,
                    checkbox_label=None,
                    column_of_second_feature=None,
                    bar_plot_xaxis_slice=None):
    prev_year = str(int(chosen_year) - 1)
    if column_of_second_feature:
        second_feature_options = data[column_of_2nd_feature].unique().tolist()

        if main_option != 'Процент молодежи, задействованной в программных мероприятиях':
            second_feature_options.insert(0, 'Все')

        second_option = st.selectbox(
            label=checkbox_label,
            options=second_feature_options
        )
        st.markdown('---')

        if second_option == 'Все':
            map_header = map_title_slice + " " + second_slice_of_title_all
            table_header = table_title_slice + second_slice_of_title_all
            top5_header = f"#### Топ 5 регионов по показателю \"{main_option}\" " + second_slice_of_title_all + \
                          f" в {chosen_year} году"
            deltas_header = f"#### Самые значительные изменения показателя \"{main_option}\" " \
                            f"{second_slice_of_title_all} по сравнению с предыдущим годом"

            grouped_df = df.groupby(['Регион', 'Показатель', 'Год']).sum(numeric_only=True).reset_index()
            table_to_show = grouped_df[grouped_df['Показатель'] == main_option]

        else:
            second_slice_of_title = f" {second_slice_of_title_specific} \"_{second_option}_\""
            map_header = map_title_slice + second_slice_of_title
            table_header = table_title_slice + second_slice_of_title
            top5_header = f"#### Топ 5 регионов по показателю \"{main_option}\"" + second_slice_of_title + \
                          f" в {chosen_year} году"
            deltas_header = f"#### Самые значительные изменения показателя \"{main_option}\" " \
                            f"{second_slice_of_title} по сравнению с предыдущим годом"

            grouped_df = df.groupby(['Регион', 'Показатель', 'Год', column_of_2nd_feature]).sum(numeric_only=True) \
                .reset_index()
            table_to_show = grouped_df[(grouped_df['Показатель'] == main_option) &
                                       (grouped_df[column_of_2nd_feature] == second_option)]

        st.markdown(map_header)

        if second_option == 'Все' or second_option is None:
            temp_df = df.groupby(['Регион', 'Показатель', 'Год']).sum(numeric_only=True).reset_index()

            temp_df = temp_df[temp_df['Показатель'] == main_option].copy()
        else:
            temp_df = df.groupby(['Регион',
                                  'Показатель', 'Год',
                                  column_of_second_feature]) \
                .sum(numeric_only=True).reset_index()

            temp_df = temp_df[(temp_df['Показатель'] == main_option) &
                              (temp_df[column_of_second_feature] == second_option)].copy()

        st.plotly_chart(map_chart(data=temp_df,
                                  geodata=geojson,
                                  first_feature=main_option,
                                  map_style=mapbox_style,
                                  colors=color_palette),
                        use_container_width=True)

        st.markdown(top5_header)
        top_regions_df = temp_df[temp_df['Год'] == chosen_year].nlargest(5, 'Значение')
        top_regions_df = top_regions_df.iloc[::-1].copy()

        if second_option == 'Все':
            tab3, tab5 = st.tabs(['Диаграмма без детализации', 'Диаграмма с детализацией'])
            with tab3:
                st.plotly_chart(bar_plot(data=top_regions_df,
                                         first_feature=main_option,
                                         second_feature=second_option),
                                use_container_width=True)
            with tab5:
                temp_temp_df = df[(df['Год'] == chosen_year) &
                                  (df['Регион'].isin(top_regions_df['Регион'])) &
                                  (df['Показатель'] == main_option)].copy()

                temp_temp_df = temp_temp_df.merge(top_regions_df.rename(columns={'Значение': 'Сумма'}),
                                                  on=['Регион'], how='left')

                st.plotly_chart(bar_plot(data=temp_temp_df.sort_values(by=['Сумма']),
                                         first_feature=main_option,
                                         second_feature=second_option,
                                         column_of_second_feature=column_of_2nd_feature,
                                         legend_text_size=9),
                                use_container_width=True)

        else:
            st.plotly_chart(bar_plot(data=top_regions_df,
                                     first_feature=main_option,
                                     second_feature=second_option,
                                     column_of_second_feature=column_of_2nd_feature,
                                     xaxis_title_slice=bar_plot_xaxis_slice),
                            use_container_width=True)

        st.markdown(f"##### Динамика показателей для топ 5 регионов в {chosen_year} году "
                    f"по показателю \"{main_option}\" сквозь года")
        st.plotly_chart(line_chart(data=temp_df[temp_df['Регион'].isin(top_regions_df['Регион'].unique())]),
                        use_container_width=True)

        if chosen_year == '2021' or chosen_year == '2020':
            st.markdown(deltas_header)
            show_delta_tables(data=temp_df, prev_year=prev_year,
                              cur_year=chosen_year)

        with st.expander(table_header):
            st.info("Вы можете отсортировать записи в таблице, нажав на поле. Также вы можете увеличить размер "
                    "таблицы, потянув за правый нижний угол")
            st.dataframe(table_to_show)

    else:
        st.markdown('---')
        top_regions_df = df[(df['Год'] == chosen_year) &
                            (df['Показатель'] == main_option)].nlargest(5, 'Значение')
        top_regions_df = top_regions_df.iloc[::-1].copy()

        st.markdown(map_title_slice)
        st.plotly_chart(map_chart(data=df[(df['Показатель'] == main_option)],
                                  geodata=geojson,
                                  first_feature=main_option,
                                  map_style=mapbox_style,
                                  colors=color_palette),
                        use_container_width=True)

        st.markdown(f"##### Топ 5 регионов по выбранному показателю {main_option} в {chosen_year} году")
        st.plotly_chart(bar_plot(data=top_regions_df,
                                 first_feature=main_option),
                        use_container_width=True)

        st.markdown(f"##### Динамика показателей для топ 5 регионов {chosen_year} года сквозь года")
        st.plotly_chart(line_chart(data=df[(df['Показатель'] == main_option) &
                                           (df['Регион'].isin(top_regions_df['Регион'].unique()))]),
                        use_container_width=True)

        temp_df = df[df['Показатель'] == main_option].copy()

        if chosen_year == '2021' or chosen_year == '2020':
            st.markdown(f"#### Самые значительные изменения показателя {main_option} по сравнению с предыдущим годом")
            show_delta_tables(data=temp_df, prev_year=prev_year,
                              cur_year=chosen_year)

        with st.expander(table_title_slice):
            st.info("Вы можете отсортировать записи в таблице, нажав на поле. Также вы можете увеличить размер "
                    "таблицы, потянув за правый нижний угол")
            st.dataframe(df[df['Показатель'] == main_option])


def show_delta_tables(data, prev_year, cur_year):
    feat_name = f'Изменение показателя с {prev_year} по {cur_year}'
    delta_df = pd.DataFrame.from_dict({'Регион': data[data['Год'] == cur_year]['Регион'].unique(),
                                       feat_name: data[data['Год'] == cur_year]["Значение"].values -
                                                  data[data['Год'] == prev_year]["Значение"].values})

    delta_df['Регион'] = delta_df['Регион'].apply(break_long_region_name)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'###### Регионы с '
                    f'наибольшим __приростом__ значения показателя :chart_with_upwards_trend: :white_check_mark:')
        st.dataframe(delta_df.nlargest(5, columns=[feat_name]))

    with col2:
        st.markdown(
            f'###### Регионы с наибольшей '
            f'__убылью__ значения показателя :chart_with_downwards_trend: :bangbang:')
        st.dataframe(delta_df.nsmallest(5, columns=[feat_name]))


def line_chart(data):
    fig = go.Figure()

    for region in data['Регион'].unique():
        df_slice = data[data['Регион'] == region].copy()
        fig.add_trace(go.Scatter(x=df_slice['Год'],
                                 y=df_slice['Значение'],
                                 name=region,
                                 mode='lines+markers',
                                 line=dict(width=2.5),
                                 marker=dict(size=7.5)
                                 ))

    fig.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0},
                      height=300,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=['2019', '2020', '2021'],
                      ))

    return fig


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


def section_for_detailed_bar_plot(data, header, column_name):
    st.markdown(header)

    region_for_bar = st.selectbox(label='Выберите регион',
                                  options=data['Регион'].unique().tolist())
    main_feature_for_bar = st.selectbox(label='Выберите показатель',
                                        options=data['Показатель'].unique().tolist())

    temp_df = data[(data['Показатель'] == main_feature_for_bar) &
                   (data['Регион'] == region_for_bar) &
                   (data['Год'] == chosen_year)].copy()

    st.plotly_chart(bar_plot_for_detailed_feature(data=temp_df.copy(deep=True),
                                                  column_name=column_name),
                    use_container_width=True)

    with st.expander(f'##### Таблица всех значений показателя \"{main_feature_for_bar}\"'):
        st.info("Вы можете отсортировать записи в таблице, нажав на поле. Также вы можете увеличить размер "
                "таблицы, потянув за правый нижний угол")
        st.dataframe(temp_df.drop(['Округ', 'Показатель'], axis=1))


def bar_plot_for_detailed_feature(data, column_name):
    data['Значение'] = data['Значение'].fillna(0)
    data = data.sort_values(by=['Значение']).copy()

    fig = go.Figure()

    fig.add_trace(go.Bar(y=data[column_name].apply(break_long_string),
                         x=data['Значение'],
                         orientation='h'))

    fig.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0},
                      legend=dict(font=dict(size=9)),
                      height=700)
    fig.update_xaxes(title=column_name)
    fig.update_yaxes()
    return fig


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
    final_df_list = []
    for year in years_to_analyze:
        temp_df = pd.read_parquet(f"data/{year}/{section_to_df[section_name]}")
        temp_df['Год'] = year
        final_df_list.append(temp_df)
    return pd.concat(final_df_list, ignore_index=True)


if __name__ == "__main__":
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto",
                       menu_items=None)
    # TODO: Добавить описание этой страницы
    st.title("Визуализация показателей")

    st.markdown("##### Для начала работы необходимо выбрать раздел и год показателей, по которым вы бы "
                "хотели видеть визуализацию данных")
    section = st.selectbox("Выберите раздел показателей",
                           options=list(section_to_df.keys()))

    chosen_year = st.selectbox('Выберите год показателей',
                               options=years_to_analyze)

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
    table_title_slice = f"##### Таблица всех значений показателя \"{main_option}\""

    if section == 'Направления реализации молодежной политики':  # P1
        column_of_2nd_feature = columns_of_2nd_feature[section]

        section_for_map(data=df,
                        second_slice_of_title_all="по всем направлениям",
                        second_slice_of_title_specific="по направлению",
                        checkbox_label="Выберите направление реализации молодежной политики",
                        column_of_second_feature=column_of_2nd_feature,
                        bar_plot_xaxis_slice='Направление')
        st.markdown('---')
        section_for_detailed_bar_plot(header=f"#### {main_option} для различных направлений "
                                             f"реализации молодежной политики в {chosen_year} году",
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
        st.markdown('---')
        section_for_detailed_bar_plot(header=f"#### {main_option} для различных видов структур "
                                             f"для показателя в {chosen_year} году",
                                      data=df,
                                      column_name=column_of_2nd_feature)

    elif section == 'Информационное обеспечение реализации молодежной политики':  # P3
        section_for_map(data=df)

    elif section == 'Общественные объединения':  # P4
        column_of_2nd_feature = columns_of_2nd_feature[section]

        section_for_map(data=df,
                        second_slice_of_title_all="для всех видов общ. объединений",
                        second_slice_of_title_specific="по виду объединений",
                        checkbox_label="Выберите вид молодежных объединений",
                        column_of_second_feature=column_of_2nd_feature,
                        bar_plot_xaxis_slice='Объединение')
        st.markdown('---')
        section_for_detailed_bar_plot(header=f"#### {main_option} для различных видов молодежных объединений"
                                             f" в {chosen_year} году",
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
        st.markdown('---')
        section_for_detailed_bar_plot(header=f"#### {main_option} для различных видов форумов "
                                             f"в {chosen_year} году",
                                      data=df,
                                      column_name=column_of_2nd_feature)

    elif section == 'Добровольчество':
        section_for_map(data=df)
        st.markdown('---')
        df2 = pd.read_parquet(f'data/{chosen_year}/p7-2.parquet')
        df3 = pd.read_parquet(f'data/{chosen_year}/p7-3.parquet')

        section_for_volunteer_pie_chart(data2=df2,
                                        data3=df3,
                                        header2="##### Распределение возрастных категорий "
                                                "граждан, вовлеченных центрами "
                                                "поддержки добровольчества",
                                        header3='##### Распределение числа '
                                                'граждан, вовлеченных в добровольческую '
                                                'деятельность, по направлениям')
