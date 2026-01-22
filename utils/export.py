import pandas as pd
from io import BytesIO

def convert_df_to_csv(df):
    """
    Converts a DataFrame to a CSV string (utf-8 encoded).
    """
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df):
    """
    Converts a DataFrame to an Excel file in memory.
    Returns:
        bytes: The Excel file content.
    """
    output = BytesIO()
    # Use xlsxwriter or openpyxl. 
    # Since openpyxl is in requirements, pandas uses it by default for .xlsx
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Projects')
    
    return output.getvalue()
