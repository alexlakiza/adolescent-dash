import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.append(".")

fed_okrug_full_names = {
    'СЗФО': 'Северо-Западного Федерального Округа',
    'ЦФО': 'Центрального Федерального Округа',
    "ЮФО": "Южного Федерального Округа",
    "СКФО": "Северо-Кавказского Федерального Округа",
    "ПФО": "Приволжского Федерального Округа",
    "УФО": "Уральского Федерального Округа",
    "СФО": "Сибирского Федерального Округа",
    "ДФО": "Дальневосточного Федерального Округа"
}

years_list = ['2019', '2020', '2021']


def break_long_string(string):
    if len(string) > 40:
        median = int(len(string) / 2)

        for i in range(15):
            if string[median + i] == ' ':
                return string[:median + i] + '<br>' + string[median + i + 1:]
    return string


def calculate_boxplot_params(array):
    q1 = np.quantile(array, q=0.25)
    median = np.median(array)
    q3 = np.quantile(array, q=0.75)
    iqr = q3 - q1

    lower_fence_lower = q1 - 1.5 * iqr
    upper_fence_upper = q3 + 1.5 * iqr

    lower_fence = max(lower_fence_lower, (array[array >= lower_fence_lower]).min())
    upper_fence = min(upper_fence_upper, (array[array <= upper_fence_upper]).max())

    return q1, median, q3, lower_fence, upper_fence


def generate_conclusion(status,
                        region,
                        feature,
                        is_lower_bad,
                        russia_or_okrug,
                        okrug=None):
    if russia_or_okrug == 'РФ':
        compare_with_rus_or_okrug = 'по сравнению с регионами России'
    else:
        if okrug:
            compare_with_rus_or_okrug = f"по сравнению с регионами {fed_okrug_full_names[okrug]}"
        else:
            compare_with_rus_or_okrug = "по сравнению с регионами Федерального Округа"

    if status == 'ok':
        st.info(f"Показатель __\"{feature}\"__ для региона __{region}__ находится в норме "
                f"{compare_with_rus_or_okrug}")
    else:
        if is_lower_bad is True:
            if status == 'good':
                st.success(f"У региона __{region}__ хороший показатель __\"{feature}\"__. "
                           f"Он немного превышает норму "
                           f"{compare_with_rus_or_okrug}", icon='✔️')
            if status == 'excellent':
                st.success(f"У региона __{region}__ превосходный показатель __\"{feature}\"__. "
                           f"Он значительно превышает норму {compare_with_rus_or_okrug}!", icon="✅")
            if status == 'bad':
                st.info(
                    f"Показатель __\"{feature}\"__ для региона __{region}__ находится "
                    f"чуть ниже нормы {compare_with_rus_or_okrug}", icon="➖")
            if status == 'awful':
                st.warning(f"У региона __{region}__ показатель __\"{feature}\"__ "
                           f"значительно ниже нормы {compare_with_rus_or_okrug}!", icon="‼️")
        elif is_lower_bad is False:
            if status == 'good':
                st.success(f"У региона __{region}__ хороший показатель __\"{feature}\"__. "
                           f"Он немного ниже нормы "
                           f"{compare_with_rus_or_okrug}", icon='✔️')
            if status == 'excellent':
                st.success(f"У региона __{region}__ превосходный показатель __\"{feature}\"__. "
                           f"Он значительно ниже нормы {compare_with_rus_or_okrug}!", icon="✅")
            if status == 'bad':
                st.info(
                    f"Показатель __\"{feature}\"__ для региона __{region}__ находится "
                    f"чуть выше нормы {compare_with_rus_or_okrug}", icon="➖")
            if status == 'awful':
                st.warning(f"У региона __{region}__ показатель __\"{feature}\"__ "
                           f"значительно превышает норму {compare_with_rus_or_okrug}!", icon="‼️")


def compare_and_show_metric(data, region, feature_name,
                            lower_values_is_bad='normal',
                            russia_or_okrug='РФ',
                            okrug=None,
                            measurement=None,
                            round_delta=True):
    q1, med, q3, lower_fence, upper_fence = calculate_boxplot_params(data[feature_name].ravel())

    current_value = data[data['Регион'] == region][feature_name].values[0]

    if russia_or_okrug == 'РФ':
        metric_okrug_part = "по сравнению с медианным значением среди всех регионов России"
    else:
        if okrug:
            metric_okrug_part = f"по сравнению с медианным значением среди регионов {fed_okrug_full_names[okrug]}"
        else:
            metric_okrug_part = "по сравнению с медианным значением среди регионов текущего Федерального Округа"

    metric_title = f"{feature_name} в регионе \"{region}\" \n\n{metric_okrug_part}"

    if lower_values_is_bad == 'normal':
        lower_worse = True
    else:
        lower_worse = False

    if round_delta:
        cur_delta = round(current_value - med)
    else:
        cur_delta = round(current_value - med, 1)

    if q1 <= current_value < med:  # lower_fence | q1 | value | med | q3 | upper_fence
        st.metric(label=metric_title,
                  value=f"{current_value} {measurement}",
                  delta=cur_delta,
                  delta_color='off')
        generate_conclusion(status='ok',
                            region=region,
                            feature=feature_name,
                            is_lower_bad=lower_worse,
                            russia_or_okrug=russia_or_okrug,
                            okrug=okrug)
    elif lower_fence <= current_value < q1:  # lower_fence | value | q1 | med | q3 | upper_fence
        st.metric(label=metric_title,
                  value=f"{current_value} {measurement}",
                  delta=cur_delta,
                  delta_color='off')
        if lower_worse:
            cur_status = 'bad'
        else:
            cur_status = 'good'
        generate_conclusion(status=cur_status,
                            region=region,
                            feature=feature_name,
                            is_lower_bad=lower_worse,
                            russia_or_okrug=russia_or_okrug,
                            okrug=okrug)
    elif current_value < lower_fence:  # value | lower_fence | q1 | med | q3 | upper_fence
        st.metric(label=metric_title,
                  value=f"{current_value} {measurement}",
                  delta=cur_delta,
                  delta_color=lower_values_is_bad)
        if lower_worse:
            cur_status = 'awful'
        else:
            cur_status = 'excellent'
        generate_conclusion(status=cur_status,
                            region=region,
                            feature=feature_name,
                            is_lower_bad=lower_worse,
                            russia_or_okrug=russia_or_okrug,
                            okrug=okrug)
    elif current_value == med:  # lower_fence | q1 | med=value | q3 | upper_fence
        st.metric(label=metric_title,
                  value=f"{current_value} {measurement}",
                  delta=None)
        generate_conclusion(status='ok',
                            region=region,
                            feature=feature_name,
                            is_lower_bad=lower_worse,
                            russia_or_okrug=russia_or_okrug,
                            okrug=okrug)
    elif med < current_value <= q3:  # lower_fence | q1 | med | value | q3 | upper_fence
        st.metric(label=metric_title,
                  value=f"{current_value} {measurement}",
                  delta=cur_delta,
                  delta_color='off')
        generate_conclusion(status='ok',
                            region=region,
                            feature=feature_name,
                            is_lower_bad=lower_worse,
                            russia_or_okrug=russia_or_okrug,
                            okrug=okrug)
    elif q3 < current_value <= upper_fence:  # lower_fence | q1 | med | q3 | value | upper_fence
        st.metric(label=metric_title,
                  value=f"{current_value} {measurement}",
                  delta=cur_delta,
                  delta_color='off')
        if lower_worse:
            cur_status = 'good'
        else:
            cur_status = 'bad'
        generate_conclusion(status=cur_status,
                            region=region,
                            feature=feature_name,
                            is_lower_bad=lower_worse,
                            russia_or_okrug=russia_or_okrug,
                            okrug=okrug)
    else:  # lower_fence | q1 | med | q3 | upper_fence | value
        st.metric(label=metric_title,
                  value=f"{current_value} {measurement}",
                  delta=cur_delta,
                  delta_color=lower_values_is_bad)
        if lower_worse:
            cur_status = 'excellent'
        else:
            cur_status = 'awful'
        generate_conclusion(status=cur_status,
                            region=region,
                            feature=feature_name,
                            is_lower_bad=lower_worse,
                            russia_or_okrug=russia_or_okrug,
                            okrug=okrug)


def section_for_analysis_of_one_feature(feature_name: str,
                                        column_name: str,
                                        region: str,
                                        okrug: str,
                                        data: pd.DataFrame,
                                        lower_is_bad: bool,
                                        x_range,
                                        measurement=None,
                                        round_delta=True):
    if region not in data['Регион'].tolist():
        st.markdown(f'Для данного региона нет данных по '
                    f'показателю \"{feature_name}\"')

    else:
        if lower_is_bad:
            lower_values_is_bad = 'normal'
        else:
            lower_values_is_bad = 'inverse'
        tab1, tab2 = st.tabs(['Сравнение со всей Россией', "Сравнение с регионами Федерального Округа"])

        year_data = data[data['Год'] == year_to_analyze].copy()
        with tab1:
            st.plotly_chart(box_plot(year_data,
                                     feature=column_name,
                                     region_to_highlight=region,
                                     scatter_style=scatter_style_option,
                                     x_range=x_range),
                            use_container_width=True)

            compare_and_show_metric(data=year_data,
                                    feature_name=column_name,
                                    region=region,
                                    lower_values_is_bad=lower_values_is_bad,
                                    measurement=measurement,
                                    round_delta=round_delta)

        with tab2:
            st.plotly_chart(box_plot(year_data[year_data['Округ'] == okrug],
                                     feature=column_name,
                                     region_to_highlight=region,
                                     scatter_style=scatter_style_option,
                                     x_range=x_range),
                            use_container_width=True)

            compare_and_show_metric(data=year_data[year_data['Округ'] == okrug],
                                    feature_name=column_name,
                                    region=region,
                                    lower_values_is_bad=lower_values_is_bad,
                                    russia_or_okrug='Округ',
                                    okrug=okrug,
                                    measurement=measurement,
                                    round_delta=round_delta)

        st.markdown(f"###### Динамика показателя \"{column_name}\" сквозь года")
        cur_region_data = data[data['Регион'] == region].copy()

        st.plotly_chart(line_chart(cur_region_data, column_name), use_container_width=True)
        if year_to_analyze == '2021':
            delta_colour = 'normal' if lower_is_bad else 'inverse'
            val_2021 = cur_region_data.loc[cur_region_data['Год'] == '2021', column_name].values[0]
            val_2020 = cur_region_data.loc[cur_region_data['Год'] == '2020', column_name].values[0]
            st.metric(label=f"Изменение показателя \"{column_name}\" по сравнению с 2020 годом",
                      value=f"{val_2021} {measurement}",
                      delta=f"{val_2021 - val_2020} {measurement}",
                      delta_color=delta_colour)
        elif year_to_analyze == '2020':
            delta_colour = 'normal' if lower_is_bad else 'inverse'
            val_2019 = cur_region_data.loc[cur_region_data['Год'] == '2019', column_name].values[0]
            val_2020 = cur_region_data.loc[cur_region_data['Год'] == '2020', column_name].values[0]
            st.metric(label=f"Изменение показателя \"{column_name}\" по сравнению с 2019 годом",
                      value=f"{val_2020} {measurement}",
                      delta=f"{val_2020 - val_2019} {measurement}",
                      delta_color=delta_colour)


def line_chart(data, column_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Год'],
                             y=data[column_name],
                             mode='lines+markers',
                             line=dict(color='blue', width=2.5),
                             marker=dict(color='blue', size=7.5),
                             name=break_long_string(column_name)))

    fig.add_trace(go.Scatter(x=[year_to_analyze],
                             y=data[data['Год'] == year_to_analyze][column_name],
                             mode='markers',
                             marker=dict(color='red', size=10, symbol='diamond'),
                             name=year_to_analyze))
    fig.update_layout(margin={"r": 0, "t": 25, "l": 0, "b": 0},
                      height=300,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=['2019', '2020', '2021'],
                      ))
    return fig


def get_df_of_n_unities_region(data: pd.DataFrame, pop_data: pd.DataFrame,
                               data_feature: str, new_feature_name: str,
                               ppl_column, year):
    temp_df = data[data['Значение'].notna()].groupby(['Регион', 'Показатель']).sum(numeric_only=True).reset_index()
    result_df = pop_data.merge(temp_df[(temp_df['Показатель'] == data_feature) & (temp_df['Значение'] != 0)],
                               on='Регион', how='inner')

    result_df[new_feature_name] = (result_df[ppl_column] / result_df['Значение']).astype(int)
    result_df['Год'] = year
    return result_df


def box_plot(data: pd.DataFrame, feature: str, region_to_highlight: str, x_range, scatter_style='Точка'):
    fig = go.Figure()

    fig.add_trace(go.Box(x=data[feature],
                         name=break_long_string(feature),
                         orientation='h',
                         quartilemethod='inclusive',
                         showlegend=False))

    if scatter_style == 'Вертикальная линия':
        fig.add_vline(x=data.loc[data['Регион'] == region_to_highlight, feature].values[0],
                      line_dash="dot",
                      line_color="red",
                      line_width=2.5,
                      annotation_text=region_to_highlight,
                      annotation_font_size=12,
                      annotation_font_color='black',
                      annotation_position="top right")

    elif scatter_style == 'Точка':
        fig.add_trace(go.Scatter(x=data.loc[data['Регион'] == region_to_highlight, feature],
                                 y=[break_long_string(feature)],
                                 mode='markers',
                                 name=region_to_highlight,
                                 marker=dict(color="red",
                                             symbol='diamond',
                                             size=10),
                                 ))
    fig.update_layout(margin={"r": 0, "t": 25, "l": 0, "b": 0},
                      height=300)
    fig.update_xaxes(range=x_range)

    return fig


if __name__ == "__main__":
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto",
                       menu_items=None)
    st.title("Аналитика по субъекту РФ")
    st.markdown("##### Для начала работы выберите субъект РФ, по которому вы бы хотели получить аналитическую сводку")

    with st.sidebar:
        p1 = st.checkbox(label='Общие показатели реализации молодежной политики',
                         value=True)
        p2 = st.checkbox(label='Структуры по работе с молодежью',
                         value=True)
        p3 = st.checkbox(label='Распространение информации о реализации молодежной политики',
                         value=True)
        p6 = st.checkbox(label='Форумы',
                         value=True)
        p7 = st.checkbox(label='Добровольчество',
                         value=True)
        with st.expander('Стиль boxplot'):
            scatter_style_option = st.radio(label='Выберите стиль отображения региона на boxplot',
                                            options=['Точка', 'Вертикальная линия'])
    pop_df = pd.read_parquet('data/population.parquet')

    chosen_region = st.selectbox(label='Выберите регион для анализа',
                                 options=pop_df['Регион'].tolist())
    year_to_analyze = st.selectbox('Выберите год показателей',
                                   options=['2021', '2020', '2019'])
    okrug_of_chose_region = pop_df.loc[pop_df['Регион'] == chosen_region, 'Округ'].values[0]

    if not any([p1, p2, p3, p6, p7]):
        st.markdown("##### Выберите показатели для анализа в боковом меню слева")

    # P1
    if p1:
        st.markdown("#### Количество детских и молодeжных общественных объединений в регионе")

        temp_df_1 = pd.concat([get_df_of_n_unities_region(pd.read_parquet(f'data/{year}/p1.parquet'),
                                                          pop_df,
                                                          'Кол-во детских и '
                                                          'молодeжных общественных объединений',
                                                          new_feature_name='Число детей и молодых '
                                                                           'людей на 1 общественное '
                                                                           'объединение',
                                                          ppl_column='Молодежь + Дети', year=year)
                               for year in years_list],
                              ignore_index=True)

        section_for_analysis_of_one_feature(feature_name='Количество детских и молодeжных общественных объединений',
                                            column_name='Число детей и молодых людей на 1 общественное объединение',
                                            region=chosen_region,
                                            okrug=okrug_of_chose_region, data=temp_df_1, lower_is_bad=False,
                                            measurement='чел.',
                                            x_range=[-10, 2750])

        st.markdown("#### Количество грантов")
        temp_dfs_list = []
        for year in years_list:
            temp_temp_df = pd.read_parquet(f'data/{year}/p1.parquet')
            temp_temp_df = temp_temp_df[temp_temp_df['Значение'].notna()].groupby(['Регион', 'Показатель']).sum(
                numeric_only=True).reset_index()
            temp_temp_df = temp_temp_df[(temp_temp_df['Показатель'] ==
                                         'Кол-во грантов')].rename(columns={'Значение': 'Кол-во грантов'}).copy()
            temp_temp_df['Год'] = year
            temp_dfs_list.append(temp_temp_df)

        temp_df_2 = pd.concat(temp_dfs_list, ignore_index=True)

        temp_df_2 = temp_df_2.merge(pop_df, on=['Регион'], how='inner')
        section_for_analysis_of_one_feature(feature_name="Количество грантов",
                                            column_name='Кол-во грантов',
                                            region=chosen_region,
                                            okrug=okrug_of_chose_region,
                                            data=temp_df_2,
                                            lower_is_bad=True,
                                            measurement='ед.',
                                            x_range=[-10, 300])

        st.divider()

    # P2
    if p2:
        temp_df_3 = pd.concat([get_df_of_n_unities_region(pd.read_parquet(f'data/{year}/p2.parquet'),
                                                          pop_df,
                                                          data_feature='Кол-во структур',
                                                          new_feature_name='Число молодых людей на 1 структуру '
                                                                           'по работе с молодежью',
                                                          ppl_column='Молодежь', year=year)
                               for year in years_list],
                              ignore_index=True)
        st.markdown("#### Количество структур по работе с молодежью")

        section_for_analysis_of_one_feature(feature_name='Количество структур по работе с молодежью',
                                            column_name='Число молодых людей на 1 структуру по работе с молодежью',
                                            region=chosen_region,
                                            okrug=okrug_of_chose_region,
                                            data=temp_df_3,
                                            lower_is_bad=False,
                                            measurement='чел.',
                                            x_range=[-100, 30000])

        st.divider()

    if p3:
        st.markdown("#### Финансирование информационного освещения реализации молодежной политики")

        temp_dfs_list_2 = []
        for year in years_list:
            temp_temp_df = pd.read_parquet(f'data/{year}/p3.parquet')
            temp_temp_df = temp_temp_df[(temp_temp_df['Показатель'] == 'Финансирование информационного '
                                                                       'освещения реализации гос. мол. политики') &
                                        (temp_temp_df['Значение'].notna())].copy()
            temp_temp_df['Год'] = year
            temp_dfs_list_2.append(temp_temp_df)

        temp_df_5 = pd.concat(temp_dfs_list_2, ignore_index=True)

        temp_df_5 = temp_df_5.rename(columns={'Значение': 'Финансирование информационного '
                                                          'освещения реализации молодежной политики'})

        section_for_analysis_of_one_feature(
            feature_name='Финансирование информационного освещения реализации молодежной политики',
            column_name='Финансирование информационного освещения реализации молодежной политики',
            region=chosen_region,
            okrug=okrug_of_chose_region,
            data=temp_df_5,
            lower_is_bad=True,
            measurement='руб.',
            x_range=[-1000, 7000000])

        st.divider()

    if p6:
        st.markdown("#### Количество молодежных форумов")
        temp_dfs_list_3 = []

        for year in years_list:
            temp_temp_df = pd.read_parquet(f'data/{year}/p6.parquet')
            temp_temp_df = temp_temp_df.groupby(['Регион', 'Показатель'])[['Значение']].sum().reset_index()
            temp_temp_df = temp_temp_df[(temp_temp_df['Показатель'] == 'Кол-во форумов')].copy()
            temp_temp_df['Год'] = year
            temp_dfs_list_3.append(temp_temp_df)

        temp_df_6 = pd.concat(temp_dfs_list_3, ignore_index=True)

        temp_df_6 = temp_df_6.rename(columns={'Значение': 'Количество форумов'}).merge(pop_df[['Регион',
                                                                                               'Округ']],
                                                                                       on=['Регион'],
                                                                                       how='inner')

        section_for_analysis_of_one_feature(
            feature_name='Количество молодежных форумов',
            column_name='Количество форумов',
            region=chosen_region,
            okrug=okrug_of_chose_region,
            data=temp_df_6,
            lower_is_bad=True,
            measurement='ед.',
            x_range=[-5, 78])

        st.divider()

    if p7:
        temp_df_7 = pd.concat([get_df_of_n_unities_region(pd.read_parquet(f'data/{year}/p7-1.parquet'),
                                                          pop_df,
                                                          data_feature='Кол-во гос. учреждений, '
                                                                       'работающих с добровольцами/волонтерами',
                                                          new_feature_name='Число человек на 1 гос. учреждение, '
                                                                           'работающее с добровольцами/волонтерами',
                                                          ppl_column='Численность', year=year)
                               for year in years_list],
                              ignore_index=True)

        st.markdown("#### Количество гос. учреждений, работающих с добровольцами/волонтерами")

        section_for_analysis_of_one_feature(feature_name='Количество гос. учреждений, '
                                                         'работающих с добровольцами/волонтерами',
                                            column_name='Число человек на 1 гос. учреждение, '
                                                        'работающее с добровольцами/волонтерами',
                                            region=chosen_region,
                                            okrug=okrug_of_chose_region,
                                            data=temp_df_7,
                                            lower_is_bad=False,
                                            measurement='чел.',
                                            x_range=[-100, 25000])

        st.markdown("#### Процент граждан, вовлеченных центрами поддержки добровольчества")
        temp_dfs_list_4 = []
        for year in years_list:
            temp_temp_df = pd.read_parquet(f'data/{year}/p7-1.parquet')

            temp_temp_df = temp_temp_df[
                (temp_temp_df['Показатель'] == 'Число граждан, вовлеченных центрами поддержки добровольчества') &
                (temp_temp_df['Значение'].notna())].copy()
            temp_temp_df = temp_temp_df.merge(pop_df.drop(['Округ'], axis=1), on=['Регион'], how='inner').copy()
            temp_temp_df['Год'] = year
            temp_temp_df['Процент граждан, вовлеченных центрами поддержки добровольчества'] = (
                    temp_temp_df['Значение'] / temp_temp_df['Численность'] * 100).round(1)

            temp_dfs_list_4.append(temp_temp_df)

        temp_df_8 = pd.concat(temp_dfs_list_4)

        section_for_analysis_of_one_feature(feature_name='Процент граждан, вовлеченных центрами '
                                                         'поддержки добровольчества',
                                            column_name='Процент граждан, вовлеченных центрами '
                                                        'поддержки добровольчества',
                                            region=chosen_region,
                                            okrug=okrug_of_chose_region,
                                            data=temp_df_8,
                                            lower_is_bad=True,
                                            measurement='% от населения региона',
                                            round_delta=False,
                                            x_range=[-1, 20])
