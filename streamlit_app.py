import streamlit as st
import pandas as pd

# Define state codes
state_codes = [
    {"State": "Andaman and Nicobar Islands", "code": "35-Andaman and Nicobar Islands", "code_number": "35"},
    {"State": "Andhra Pradesh", "code": "37-Andhra Pradesh", "code_number": "37"},
    {"State": "Arunachal Pradesh", "code": "12-Arunachal Pradesh", "code_number": "12"},
    {"State": "Assam", "code": "18-Assam", "code_number": "18"},
    {"State": "Bihar", "code": "10-Bihar", "code_number": "10"},
    {"State": "Chandigarh", "code": "04-Chandigarh", "code_number": "04"},
    {"State": "Chhattisgarh", "code": "22-Chhattisgarh", "code_number": "22"},
    {"State": "Dadra and Nagar Haveli and Daman and Diu", "code": "26-Dadra and Nagar Haveli and Daman and Diu", "code_number": "26"},
    {"State": "Daman and Diu", "code": "25-Daman and Diu", "code_number": "25"},
    {"State": "Delhi", "code": "07-Delhi", "code_number": "07"},
    {"State": "Goa", "code": "30-Goa", "code_number": "30"},
    {"State": "Gujarat", "code": "24-Gujarat", "code_number": "24"},
    {"State": "Haryana", "code": "06-Haryana", "code_number": "06"},
    {"State": "Himachal Pradesh", "code": "02-Himachal Pradesh", "code_number": "02"},
    {"State": "Jammu and Kashmir", "code": "01-Jammu and Kashmir", "code_number": "01"},
    {"State": "Jharkhand", "code": "20-Jharkhand", "code_number": "20"},
    {"State": "Karnataka", "code": "29-Karnataka", "code_number": "29"},
    {"State": "Kerala", "code": "32-Kerala", "code_number": "32"},
    {"State": "Ladakh", "code": "38-Ladakh", "code_number": "38"},
    {"State": "Lakshadweep", "code": "31-Lakshadweep", "code_number": "31"},
    {"State": "Madhya Pradesh", "code": "23-Madhya Pradesh", "code_number": "23"},
    {"State": "Maharashtra", "code": "27-Maharashtra", "code_number": "27"},
    {"State": "Manipur", "code": "14-Manipur", "code_number": "14"},
    {"State": "Meghalaya", "code": "17-Meghalaya", "code_number": "17"},
    {"State": "Mizoram", "code": "15-Mizoram", "code_number": "15"},
    {"State": "Nagaland", "code": "13-Nagaland", "code_number": "13"},
    {"State": "Odisha", "code": "21-Odisha", "code_number": "21"},
    {"State": "Other Territory", "code": "97-Other Territory", "code_number": "97"},
    {"State": "Puducherry", "code": "34-Puducherry", "code_number": "34"},
    {"State": "Punjab", "code": "03-Punjab", "code_number": "03"},
    {"State": "Rajasthan", "code": "08-Rajasthan", "code_number": "08"},
    {"State": "Sikkim", "code": "11-Sikkim", "code_number": "11"},
    {"State": "Tamil Nadu", "code": "33-Tamil Nadu", "code_number": "33"},
    {"State": "Telangana", "code": "36-Telangana", "code_number": "36"},
    {"State": "Tripura", "code": "16-Tripura", "code_number": "16"},
    {"State": "Uttar Pradesh", "code": "09-Uttar Pradesh", "code_number": "09"},
    {"State": "Uttarakhand", "code": "05-Uttarakhand", "code_number": "05"},
    {"State": "West Bengal", "code": "19-West Bengal", "code_number": "19"}
]

# Function to process the Excel file
def process_excel(file):
    try:
        # Load the Excel file
        sheet_7A2 = pd.read_excel(file, sheet_name='Section 7(A)(2) in GSTR-1')
        sheet_7B2 = pd.read_excel(file, sheet_name='Section 7(B)(2) in GSTR-1')
        
        # Extract and rename columns from Section 7(B)(2) in GSTR-1
        cleaned_df = sheet_7B2[['Delivered State (PoS)', 'Aggregate Taxable Value Rs.', 'IGST %']].copy()
        cleaned_df.columns = ['State', 'Base', 'Tax Rate']
        
        # Create a dictionary for quick lookup of state codes
        state_code_map = {str(item['code_number']).zfill(2): item['State'] for item in state_codes}
        
        # Extract the first two digits from the GSTIN column in Section 7(A)(2) in GSTR-1 and map to State
        sheet_7A2['State'] = sheet_7A2['GSTIN'].str[:2].map(state_code_map)
        
        # Sum CGST % and SGST/UT % to get the Tax Rate
        sheet_7A2['Tax Rate'] = sheet_7A2['CGST %'] + sheet_7A2['SGST/UT %']
        
        # Select relevant columns and rename them
        df_7A2_cleaned = sheet_7A2[['State', 'Aggregate Taxable Value Rs.', 'Tax Rate']].copy()
        df_7A2_cleaned.columns = ['State', 'Base', 'Tax Rate']
        
        # Append the cleaned data from Section 7(A)(2) to cleaned_df
        cleaned_df = pd.concat([cleaned_df, df_7A2_cleaned], ignore_index=True)
        
        # Create a reverse map where the key is the state name and the value is the state code
        state_name_to_code_map = {item['State']: item['code'] for item in state_codes}
        
        # Now, replace the state names in cleaned_df with their corresponding codes
        cleaned_df['State'] = cleaned_df['State'].map(state_name_to_code_map)
        
        # Create the new dataframe with specified column names
        final_df = pd.DataFrame({
            'Type': 'OE',
            'Place Of Supply': cleaned_df['State'],
            'Rate': cleaned_df['Tax Rate'],
            'Applicable % of Tax Rate': '',
            'Taxable Value': cleaned_df['Base'],
            'Cess Amount': '',
            'E-Commerce GSTIN': ''
        })
        
        return final_df
    
    except Exception as e:
        st.error(f"Error occurred: {e}")

# Streamlit UI code
st.title("Excel to CSV Converter")
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = process_excel(uploaded_file)
    
    if df is not None:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='b2cs.csv',
            mime='text/csv'
        )
