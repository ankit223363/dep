
import pandas as pd
import json
import os
from datetime import datetime

def convert_datetime(value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    return value

def clean_dataframe(df):
    df = df.dropna(how='all').reset_index(drop=True)
    desired_columns = ['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4']
    existing_columns = [col for col in desired_columns if col in df.columns]
    df = df[existing_columns]
    df = df.dropna(subset=existing_columns, how='all')
    df = df[~df.apply(lambda row: all(str(value).strip() == '' for value in row), axis=1)]

    header_values = ['Module', 'Composant', 'Tag de livraison']
    if df.iloc[0].tolist() == header_values:
        df = df.iloc[1:]

    df = df.dropna()
    df = df[~df.apply(lambda row: any(str(value).strip() == '' for value in row), axis=1)]
    df = df[df['Unnamed: 3'].str.strip().str.lower() != 'frontend']
    df['module'] = df['Unnamed: 2'].astype(str).str.strip() + '-' + df['Unnamed: 3'].astype(str).str.strip()
    df = df.rename(columns={'Unnamed: 4': 'version'})
    df = df.drop(columns=['Unnamed: 2', 'Unnamed: 3'])
    df = df[['module', 'version']]

    return df

def clean_livraison_echanges(df):
    df = df.iloc[3:].reset_index(drop=True)
    df = df[[1, 2]]
    df = df.rename(columns={1: 'module', 2: 'version'})
    df = df.dropna()
    df = df[~df.apply(lambda row: any(str(value).strip() == '' for value in row), axis=1)]
    return df.reset_index(drop=True)

def process_excel_to_json(file_path):
    output_paths = []
    try:
        df1 = pd.read_excel(file_path, sheet_name="Livraison Modules")
        df1 = clean_dataframe(df1)
        df1 = df1.map(convert_datetime)
        data1 = {"data": df1.to_dict(orient='records')}
        output_file_1 = os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0] + '_clean.json')
        with open(output_file_1, 'w', encoding='utf-8') as f:
            json.dump(data1, f, indent=4, ensure_ascii=False)
        output_paths.append(output_file_1)

        df2 = pd.read_excel(file_path, sheet_name="Livraison echanges", header=None)
        df2 = clean_livraison_echanges(df2)
        df2 = df2.map(convert_datetime)
        data2 = {"data": df2.to_dict(orient='records')}
        output_file_2 = os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0] + '_clean-module.json')
        with open(output_file_2, 'w', encoding='utf-8') as f:
            json.dump(data2, f, indent=4, ensure_ascii=False)
        output_paths.append(output_file_2)

        return output_paths
    except Exception as e:
        raise RuntimeError(f"Error processing Excel: {e}")
