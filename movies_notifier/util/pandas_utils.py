import pandas as pd


def console_settings():
    pd.set_option('display.max_colwidth', 300)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)


def split_json_field(df, field):
    df_json = pd.read_json('[%s]' % ','.join(df[field].astype(str).tolist()))
    df_out = pd.concat([df.reset_index(drop=True), df_json], axis=1)
    df_out.drop(field, axis=1, inplace=True)
    return df_out

