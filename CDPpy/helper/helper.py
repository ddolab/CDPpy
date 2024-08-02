import pandas as pd
import numpy as np
import os, re
from pathlib import Path

def remove_units(text):
    modified_text = re.sub(r'\s*\(.*?\)', '', text)
    return modified_text

def compile_df(df):
    # Remove ".X" from Cell Line Name. X is a number.
    pattern = re.compile(r'\.\d+')
    cell_lines = [pattern.sub('', s) for s in df.columns][1:]
    # Transpose df, rename columns and insert "Cell Line" column at first.
    df_T = df.T.reset_index(drop=True)
    new_cols = df_T.iloc[0]
    df = df_T.iloc[1:]
    df.columns = new_cols
    df.insert(0, 'Cell Line', cell_lines)
    return df

def add_descriptive_column(df, name):
    '''add the row of the column that describes the dataframe.'''
    col_df = pd.DataFrame(data=dict(zip(df.columns, [[col] for col in df.columns])))
    new_df = pd.concat([col_df, df], axis=0, ignore_index=True)
    new_column_names = {col: '' if i != 0 else name for i, col in enumerate(df.columns)}
    new_df = new_df.rename(columns=new_column_names)
    return new_df

def split_name_unit(string):
    '''Split the string into the parameter name and its unit using regular expression.
    '''
    pattern = r"(\(.*\))"
    match = re.search(pattern, string)
    if match:
        splits = re.split(pattern, string)
        return splits[0][:-1], splits[1]
    else:
        return string, ''

def create_value_unit_df(data):
    '''Create DataFrame with value and its unit.'''
    df = data.copy().to_frame()
    col_name = df.columns[0]
    name, unit = split_name_unit(col_name)
    df = df.rename(columns={col_name: 'value'})
    df['unit'] = unit
    df.index.name = col_name
    return df

def split_df(df, target_columns) -> list:
    '''Split a DataFrame by the target columns, and returns the list of DataFrames.
    '''
    indices = [i for i, col in enumerate(df.columns) if col in target_columns]
    indices.append(df.shape[1])
    
    df_list = []
    for i in range(1, len(indices)):
        temp = df.iloc[1:, indices[i-1]:indices[i]]
        temp.set_axis(df.iloc[0, indices[i-1]:indices[i]], axis=1, inplace=True)
        df_list.append(temp.reset_index(drop=True))
    return df_list

def get_measurement_indices(data):
    '''Get indices of the data where measurement exist.'''
    return data[data.notnull()].index.values

def create_col_indices(df) -> dict[str, str]:
    '''Create the dictionary of column indices and units.
    '''
    column_indices = {}
    for i, col in enumerate(df.columns):
        name, unit = split_name_unit(col)
        column_indices[name] = {'index': i, 'unit': unit}
    return column_indices

def create_df_dict(df, columns, col_indices) -> dict[str, pd.DataFrame]:
    '''Create the dictionary of the DataFrame
    '''
    df_dict = {}
    for col_name in columns:
        index = col_indices[col_name]['index']
        unit = col_indices[col_name]['unit']
        temp = df.iloc[:, index].copy().to_frame(name='value').astype('float')
        temp['unit'] = unit
        temp.index.name = col_name
        df_dict[col_name] = temp
    return df_dict

###########################################################################
# Check Error for Pandas
def check_key(df, key):
    try:
        return (df[key])
    except Exception as e:
        # print(f'Error {e}')
        return pd.Series(data=np.nan)
###########################################################################

###########################################################################
# Check Input File Path
def input_path(file_name):
    # Base directry where this file exits
    BASE_DIR = Path(__file__).resolve().parent

    # Input directry path
    INPUT_BASE = os.path.join(BASE_DIR.parent.parent, 'input_files')

    # Input file path
    INPUT_FILE_PATH = os.path.join(INPUT_BASE, file_name)
    
    return INPUT_FILE_PATH
###########################################################################

###########################################################################
# Check Output File Path
def output_path(file_name):
    # Base directry where this file exits
    BASE_DIR = Path(__file__).resolve().parent

    # Input directry path
    OUTPUT_BASE = os.path.join(BASE_DIR.parent.parent, 'output_files')

    # Make output files directry
    try:
        os.makedirs(OUTPUT_BASE)    
        print("Directory " , OUTPUT_BASE ,  " Created ")
    except FileExistsError:
        pass
        # print("Directory " , OUTPUT_BASE ,  " already exists")

    # Input file path
    OUTPUT_FILE_PATH = os.path.join(OUTPUT_BASE, file_name)
    
    return OUTPUT_FILE_PATH