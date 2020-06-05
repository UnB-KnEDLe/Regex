from os import listdir
from os.path import isfile, join

# def print_database_dfs(files_path, ato):
#     res_dfs = []
#     for txt in files_path:
#         txt_str = open(txt, "r").read()
#         ret = Retirements(txt_str)
#         if not ret.data_frame.empty:
#             res_dfs.append(ret.data_frame)

#     rets_final = pd.concat([pd.DataFrame(df) for df in res_dfs],
#                             ignore_index=True)
#     print_dataframe(rets_final)

def print_dataframe(df):
    style_df = (df.style.set_properties(**{'text-align': 'left'})
                                        .set_table_styles([ dict(selector='th',
                                                                 props=[('text-align','left')])])
                   )
    return style_df

def get_txts(path):
    years = [join(path, x) for x in listdir(path) if not isfile(join(path, x))]
    txts = []
    for year in years:
        months = [join(year, x) for x in listdir(year) if not isfile(join(year, x))]
        for month in months:
            txts += [join(month, x) for x in listdir(month) if isfile(join(month, x))]
    return txts