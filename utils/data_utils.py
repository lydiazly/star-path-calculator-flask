# -*- coding: utf-8 -*-
# utils/data_utils.py
"""Functions used only for preparing the data."""
import pandas as pd
# import pickle
import os

__all__ = []


data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def convert_id(id_value) -> str:
    """Converts Bayer Designation IDs for consistency.

    Examples:
      a --> alf
      e --> eps
      m --> mu.
      m1 --> mu.01
      38 --> 38
      V640 --> V640
    """
    import json
    with open(os.path.join(data_dir, 'greek_map.json'), 'r') as file:
        greek_map = json.load(file)

    if id_value.isdigit():
        return id_value

    result = []
    num_str = ""
    for char in id_value:
        # Convert lowercase Latin letters to Greek abbreviation (no 'f', 'j', and 'v' found in the source file)
        if char.islower():
            result.append(greek_map.get(char, char))
        # Collect digits
        elif char.isdigit():
            num_str += char
        # Retain uppercase Latin letters and other characters
        else:
            result.append(char)

    # Pad the numeric part to 2 digits
    if num_str:
        result.append(f"{int(num_str):02d}")

    return "".join(result)


def join_pinyin_syllables(syllable_list: list) -> str:
    """Helper function to join pinyin syllables."""
    vowels = {'a', 'e', 'i', 'o', 'u'}
    result = syllable_list[0].title()
    for i in range(1, len(syllable_list)):
        # Add an apostrophe if the next syllable begins with a vowel
        if syllable_list[i][0] in vowels:
            result += "'"
        result += syllable_list[i].title() if syllable_list[i-1][0] == '(' else syllable_list[i]
    return result


def process_pinyin(text: str) -> str:
    """Helper function to process pinyin."""
    from pypinyin import pinyin, load_phrases_dict, Style
    # from pypinyin_dict.phrase_pinyin_data import large_pinyin
    from pypinyin_dict.phrase_pinyin_data import zdic_cibs
    import itertools
    import json

    with open(os.path.join(data_dir, 'pinyin_overwrite.json'), 'r') as file:
        pinyin_overwrite = json.load(file)

    zdic_cibs.load()
    load_phrases_dict(pinyin_overwrite)

    pinyin_list = list(itertools.product(*pinyin(text, style=Style.NORMAL, heteronym=True, v_to_u=True)))
    # pinyin_str = ','.join([join_pinyin_syllables(w) for w in pinyin_list]).replace('ü', 'u')
    pinyin_str = ','.join([join_pinyin_syllables(w) for w in pinyin_list])  # Retains 'ü'
    # pinyin_with_tone_list = list(itertools.product(*pinyin(text, heteronym=True, v_to_u=True)))
    # pinyin_with_tone_str = ','.join([' '.join([c.title() for c in w]) for w in pinyin_with_tone_list])
    return pinyin_str


def get_pinyin(text: str) -> str:
    """Converts a word to pinyin."""
    if pd.isnull(text) or text == '':
        return ''

    if '/' in text:
        pinyin_combined = '/'.join([process_pinyin(s) for s in text.split('/')])
    else:
        pinyin_combined = process_pinyin(text)

    print(f'{text}\t{pinyin_combined}')
    return pinyin_combined


def load_name_zh() -> pd.DataFrame:
    """Reads the table containing Traditional Chinese names then add Simplified Chinese and pinyin columns."""
    # df = pd.read_csv(os.path.join(data_dir, 'star-name-zh.csv'))
    # df.sort_values(by=['Const', 'Id', 'Name_en'], inplace=True)
    # df.reset_index(drop=True, inplace=True)
    # df_to_csv(df, 'star-name-zh_sorted.csv')
    df = pd.read_csv(os.path.join(data_dir, 'star-name-zh_sorted.csv'))

    df['Id_new'] = df['Id'].apply(convert_id)
    df['Bayer Designation'] = df['Id_new'] + "_" + df['Const']
    df['Name_zh_hk'] = df['Name_zh_hk'].str.replace(r'\s*,\s*', '/', regex=True)
    df = df[df['Name_zh_hk'].notna() & (df['Name_zh_hk'] != '')]  # Remove rows where 'Name_zh_hk' is empty or null
    df_name_zh = df[['Bayer Designation', 'Name_zh_hk']]
    df_name_zh = df_name_zh.drop_duplicates()

    # Add Simplified Chinese column
    import opencc
    converter = opencc.OpenCC('hk2s.json')  # Traditional (HK) to simplified
    df_name_zh['Name_zh'] = df_name_zh['Name_zh_hk'].apply(converter.convert)

    # Add pinyin column
    df_name_zh['Pinyin'] = df_name_zh['Name_zh'].apply(get_pinyin)
    df_to_csv(df_name_zh, 'bayer-zh.csv')
    return df_name_zh


def load_hip_ident() -> pd.DataFrame:
    """Merges proper names and Bayer Designations with Chinese names.

    Does the following:
    1. Read proper names, Bayer Designations, and Chinese names from files.
    2. Correct Bayer Designations.
    3. Group by HIP and merge on HIP.
    4. Combine names into a single 'name' column.
    5. Save to 'hip_ident_zh.csv' and returns the DataFrame.
    """
    import numpy as np

    # Read proper names and Bayer Designations --------------------------------|
    df_bayer = pd.read_pickle(os.path.join(data_dir, 'ident_bayer.pkl'))
    df_bayer_add = pd.read_csv(os.path.join(data_dir, 'ident_bayer_add.csv'))  # additional table
    df_proper = pd.read_pickle(os.path.join(data_dir, 'ident_proper.pkl'))
    # df_to_csv(df_bayer, 'ident_bayer.csv')
    # df_to_csv(df_proper, 'ident_proper.csv')

    # Read Chinese names ------------------------------------------------------|
    # df_name_zh_matched = load_name_zh()  # also save to 'bayer-zh.csv'
    df_name_zh_matched = pd.read_csv(os.path.join(data_dir, 'bayer-zh.csv'))
    df_name_zh_matched['HIP'] = ''
    df_name_zh_matched['Mark'] = ''
    df_name_zh_columns = df_name_zh_matched.columns.tolist()

    # Correct Bayer Designations (first match) --------------------------------|
    df_name_zh_corrections = pd.read_csv(os.path.join(data_dir, 'bayer-zh-corrections.csv'))
    df_name_zh_corrections.set_index('Name_zh_hk', inplace=True)
    df_name_zh_matched.set_index('Name_zh_hk', inplace=True)
    df_name_zh_matched.update(df_name_zh_corrections)
    df_name_zh_matched.reset_index(inplace=True)
    df_name_zh_matched = df_name_zh_matched[df_name_zh_columns].drop_duplicates()

    # Iterate over each df_name_zh_matched['Bayer Designation'] to match with df_bayer['Bayer Designation']
    for idx, bayer_id in enumerate(df_name_zh_matched['Bayer Designation']):
        matches = df_bayer[df_bayer['Bayer Designation'] == bayer_id]
        if len(matches) > 0:
            df_name_zh_matched.at[idx, 'HIP'] = matches.iloc[0]['HIP']  # Take the first match
            if len(matches) > 1:
                df_name_zh_matched.at[idx, 'Mark'] = 'MULT'  # Multiple matches found
        else:
            matches = df_bayer_add[df_bayer_add['Bayer Designation'] == bayer_id]
            if len(matches) > 0:
                df_name_zh_matched.at[idx, 'HIP'] = matches.iloc[0]['HIP']
            else:
                df_name_zh_matched.at[idx, 'Mark'] = 'NA'  # No match found
    # Save the intermediate table containing Chinese names and Bayer Designations
    df_to_csv(df_name_zh_matched, 'bayer-zh-hip.csv')

    # Group by HIP ------------------------------------------------------------|
    # Aggregate Bayer Designation and Proper Name with '/'
    df_bayer_agg = df_bayer.groupby('HIP')['Bayer Designation'].apply(lambda x: '/'.join(x)).reset_index()
    df_proper_agg = df_proper.groupby('HIP')['Proper Name'].apply(lambda x: '/'.join(x)).reset_index()

    # Merge the DataFrames on the HIP column ----------------------------------|
    df_merged = pd.merge(df_bayer_agg, df_proper_agg, on='HIP', how='outer')
    # df_merged = pd.merge(df_merged, df_name_zh_matched[['HIP', 'Name_zh_hk', 'Name_zh', 'Pinyin']], on='HIP', how='left')
    df_name_zh_filtered = df_name_zh_matched[df_name_zh_matched['HIP'].notnull()]
    df_merged = pd.merge(df_merged, df_name_zh_filtered[['HIP', 'Bayer Designation', 'Name_zh_hk', 'Name_zh', 'Pinyin']],
                         on='HIP', how='outer', suffixes=('', '_new'))

    # Only update the 'Bayer Designation' if it's missing in df_merged
    df_merged['Bayer Designation'] = np.where(
        (df_merged['HIP'].isin(df_name_zh_filtered['HIP'])) &
        (~df_merged['HIP'].isin(df_merged.dropna(subset=['Bayer Designation'])['HIP'])),
        df_merged['Bayer Designation_new'], df_merged['Bayer Designation']
    )

    # Drop the temporary 'Bayer Designation_new' column
    df_merged.drop(columns=['Bayer Designation_new'], inplace=True)

    # Fill NaN values with empty strings
    df_merged['Bayer Designation'] = df_merged['Bayer Designation'].fillna('')
    df_merged['Proper Name'] = df_merged['Proper Name'].fillna('')
    df_merged['Name_zh_hk'] = df_merged['Name_zh_hk'].fillna('')
    df_merged['Name_zh'] = df_merged['Name_zh'].fillna('')
    df_merged['Pinyin'] = df_merged['Pinyin'].fillna('')

    # Combine names into a single 'name' column -------------------------------|
    df_merged['name'] = df_merged['Bayer Designation'] + '/' + df_merged['Proper Name']
    df_merged['name'] = df_merged['name'].str.strip('/').str.replace('//', '/')

    # Select only the required columns and rename them ------------------------|
    df_merged = df_merged[['HIP', 'name', 'Name_zh', 'Name_zh_hk', 'Pinyin']]
    df_merged.columns = ['hip', 'name', 'name_zh', 'name_zh_hk', 'pinyin']

    # Output ------------------------------------------------------------------|
    df_to_csv(df_merged, 'hip_ident_zh.csv')

    return df_merged


def df_to_json(df: pd.DataFrame, filename='hip_ident.json'):
    import json
    data_dict = df.to_dict(orient='records')
    with open(os.path.join(data_dir, filename), 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)
        json_file.write("\n")


def df_to_csv(df: pd.DataFrame, filename='hip_ident.csv'):
    df.to_csv(os.path.join(data_dir, filename), index=False)


def csv_to_json(input_filename='hip_ident_zh.csv'):
    basename = os.path.splitext(input_filename)[0]
    df = pd.read_csv(os.path.join(data_dir, f'{basename}.csv'))
    df = df.fillna('')
    df_to_json(df, f'{basename}.json')


def hip_validation(hip_min=None, hip_max=None):
    """ Validates HIP in the data source.

    HIP range: [1, 120416]
    first/last HIP: 1/118322
    entries: 118218
    missing in [1, 118322]: 138
    valid: 117955
    mag_nan: 1, ra_nan: 263, dec_nan: 263
    """
    import numpy as np
    import core.data_loader as dl

    idx = dl.hip_df.index
    hip_first = dl.hip_df.head(1).index.item()
    hip_last = dl.hip_df.tail(1).index.item()
    if hip_min is None:
        hip_min = dl.hip_df.index.min()
    if hip_max is None:
        hip_max = dl.hip_df.index.max()

    count_in = 0
    count_valid = 0
    count_mag_nan = 0
    count_ra_nan = 0
    count_dec_nan = 0
    count_missing = 0
    for i in range(hip_min, hip_max+1):
        if i in idx:
            count_in += 1
            s = dl.hip_df.loc[i]
            if any([np.isnan(s['magnitude']), np.isnan(s['ra_degrees']), np.isnan(s['dec_degrees'])]):
                if np.isnan(s['magnitude']):
                    count_mag_nan += 1
                if np.isnan(s['ra_degrees']):
                    count_ra_nan += 1
                if np.isnan(s['dec_degrees']):
                    count_dec_nan += 1
                print(f"- hip={i}: mag={s['magnitude']}, radec=({s['ra_degrees']}, {s['dec_degrees']})")
            else:
                count_valid += 1
                if i < hip_first or i > hip_last:
                    print(f"+ hip={i}: mag={s['magnitude']}, radec=({s['ra_degrees']}, {s['dec_degrees']})")
        elif i >= hip_first and i <= hip_last:
            count_missing += 1
            print(f"* hip={i}: no entry")

    print(f"\nHIP range: [{hip_min}, {hip_max}]")
    print(f"first/last HIP: {hip_first}/{hip_last}")
    print(f"entries: {count_in}")
    print(f"missing in [{hip_first}, {hip_last}]: {count_missing}")
    print(f"valid: {count_valid}")
    print(f"mag_nan: {count_mag_nan}, ra_nan: {count_ra_nan}, dec_nan: {count_dec_nan}")


def docx_to_pkl():
    """Reads docx files and saves the entries to pkl files."""
    try:
        from docx import Document
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Module docx not found. Install by:\npython -m pip install python-docx")

    col_name = "Proper Name"
    doc_name = "ident6.docx"
    out_name = "ident_proper.pkl"

    # col_name = "Bayer Designation"
    # doc_name = "ident4.docx"
    # out_name = "ident_bayer.pkl"

    doc = Document(os.path.join(data_dir, doc_name))
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)

    df = pd.DataFrame(columns={col_name: str, "HIP": int})

    for i in range(len(full_text)):
        a, b = full_text[i].split('|')
        df.loc[i] = [a.strip(), int(b.strip())]

    df.to_pickle(os.path.join(data_dir, out_name))
