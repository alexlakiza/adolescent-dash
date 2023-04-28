import pandas as pd

xl = pd.ExcelFile('../init_data/Бюллетень_2021.xlsx')

ls = xl.sheet_names

final_dict = {}
counter = 0

for i in range(1, 9):
    available_regions_for_okrug = list(filter(lambda x: x.startswith(f'2.{i}.'), ls))

    for j in available_regions_for_okrug[1:]:
        temp_df = pd.read_excel('../init_data/Бюллетень_2021.xlsx', sheet_name=j)
        region = temp_df.loc[0, 'ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  \n на 1 января 2021 года ']
        print(region)

        year14_people = temp_df.loc[temp_df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '
                                            '\n на 1 января 2021 года '] == '14', 'Unnamed: 1'].values[0]
        year15_34_people = temp_df.loc[temp_df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '
                                               '\n на 1 января 2021 года '] == '15 – 34', 'Unnamed: 1'].values[0]
        year35_people = temp_df.loc[temp_df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '
                                            '\n на 1 января 2021 года '] == '35', 'Unnamed: 1'].values[0]

        year0_13_people = temp_df.loc[temp_df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '
                                              '\n на 1 января 2021 года '] == '0 – 13', 'Unnamed: 1'].values[0]

        n_youth_people = year14_people + year15_34_people + year35_people

        n_kids = temp_df.loc[temp_df['ЧИСЛЕННОСТЬ НАСЕЛЕНИЯ ПО ПОЛУ И ВОЗРАСТУ  '
                                     '\n на 1 января 2021 года '] == '0 – 17', 'Unnamed: 1'].values[0]

        n_youth_plus_kids = n_youth_people + year0_13_people

        region_dict = {'Регион': region,
                       'Молодежь': n_youth_people,
                       'Дети': n_kids,
                       'Молодежь + Дети': n_youth_plus_kids}

        final_dict[counter] = region_dict
        counter += 1

df = pd.DataFrame(final_dict).T

df.to_parquet('../data/population_by_age.parquet', index=False)
