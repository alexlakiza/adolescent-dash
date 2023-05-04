import pandas as pd  # Импорт необходимой для работы библиотеки

# Чтение excel-файла
ls = pd.ExcelFile('../init_data/Бюллетень_2021.xlsx').sheet_names  # Список листов excel-файла

final_dict = {}  # Словарь, в котором будут храниться данные о каждом регионе
counter = 0  # Переменная для индексации регионов

for fed_okr in range(1, 9):  # Итерация по восьми Федеральным округам
    available_regions_for_okr = list(filter(lambda x: x.startswith(f'2.{fed_okr}.'), ls))
    for subject_rf in available_regions_for_okr[1:]:  # Итерация по всем субъектам текущего Фед. Округа
        # Чтение конкретного листа excel-файла
        df = pd.read_excel('../init_data/Бюллетень_2021.xlsx', sheet_name=subject_rf)
        # Текущий регион
        region = df.loc[0, 'ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  \n на 1 января 2021 года ']

        # Извлечение данных о возрастных группах
        year14_people = df.loc[df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '  # Число 14-летних людей
                                  '\n на 1 января 2021 года '] == '14', 'Unnamed: 1'].values[0]
        year15_34_people = df.loc[df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И '  # Число людей в возрасте 15-34 
                                     'ВОЗРАСТУ  \n на 1 января 2021 года '] == '15 – 34', 'Unnamed: 1'].values[0]
        year35_people = df.loc[df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И '  # Число 35-летних людей
                                  'ВОЗРАСТУ  \n на 1 января 2021 года '] == '35', 'Unnamed: 1'].values[0]
        year0_13_people = df.loc[df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '  # Число детей от 0 до 13 лет
                                    '\n на 1 января 2021 года '] == '0 – 13', 'Unnamed: 1'].values[0]
        n_youth_people = year14_people + year15_34_people + year35_people  # Численность молодежи
        n_kids = df.loc[df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '  # Численность детей
                           '\n на 1 января 2021 года '] == '0 – 17', 'Unnamed: 1'].values[0]
        n_youth_plus_kids = n_youth_people + year0_13_people  # Число людей в возрасте от 0 до 35 лет включительно

        region_dict = {'Регион': region, 'Молодежь': n_youth_people,
                       'Дети': n_kids, 'Молодежь + Дети': n_youth_plus_kids}

        final_dict[counter] = region_dict
        counter += 1

final_df = pd.DataFrame(final_dict).T  # Формирование и экспорт набора данных с численностью людей
final_df.to_parquet('../data/population_by_age.parquet', index=False)

