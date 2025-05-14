import glob
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3

log_file = "log_file.txt"
target_file = "transformed_data.csv"
db_name = "STAFF.db"  # Connect to STAFF.db from your earlier question

def log_progress(message):
    timestamp_format = '%Y-%m-%d-%H:%M:%S'  # Changed %h to %m for numeric month
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    log_message = f"{timestamp},{message}"
    print(f"LOG: {log_message}")  # Print to terminal for visibility
    with open(log_file, "a") as f:
        f.write(log_message + '\n')

def extract_from_csv(file_to_process):
    try:
        dataframe = pd.read_csv(file_to_process)
        print(f"Processing CSV: {file_to_process}, Columns: {list(dataframe.columns)}")

        # Map columns (adjust based on your data)
        column_mapping = {
            'FirstName': 'name',  # Combine FirstName and LastName if needed
            'Height': 'height',
            'Weight': 'weight'
        }
        # If FirstName and LastName exist, combine them into name
        if 'FirstName' in dataframe.columns and 'LastName' in dataframe.columns:
            dataframe['name'] = dataframe['FirstName'] + ' ' + dataframe['LastName']
        elif 'FirstName' in dataframe.columns:
            dataframe['name'] = dataframe['FirstName']

        # Rename columns and select only name, height, weight
        dataframe = dataframe.rename(columns=column_mapping)
        required_columns = ['name', 'height', 'weight']
        if not all(col in dataframe.columns for col in required_columns):
            log_progress(f"Skipping {file_to_process}: Missing required columns {required_columns}")
            return pd.DataFrame(columns=required_columns)
        dataframe = dataframe[required_columns]
        print(f"Extracted from {file_to_process}:\n{dataframe}")
        return dataframe
    except Exception as e:
        log_progress(f"Error processing CSV {file_to_process}: {str(e)}")
        return pd.DataFrame(columns=['name', 'height', 'weight'])

def extract_from_json(file_to_process):
    try:
        dataframe = pd.read_json(file_to_process, lines=True)
        print(f"Processing JSON: {file_to_process}, Columns: {list(dataframe.columns)}")

        # Map columns
        column_mapping = {
            'FirstName': 'name',
            'Height': 'height',
            'Weight': 'weight'
        }
        if 'FirstName' in dataframe.columns and 'LastName' in dataframe.columns:
            dataframe['name'] = dataframe['FirstName'] + ' ' + dataframe['LastName']
        elif 'FirstName' in dataframe.columns:
            dataframe['name'] = dataframe['FirstName']

        dataframe = dataframe.rename(columns=column_mapping)
        required_columns = ['name', 'height', 'weight']
        if not all(col in dataframe.columns for col in required_columns):
            log_progress(f"Skipping {file_to_process}: Missing required columns {required_columns}")
            return pd.DataFrame(columns=required_columns)
        dataframe = dataframe[required_columns]
        print(f"Extracted from {file_to_process}:\n{dataframe}")
        return dataframe
    except Exception as e:
        log_progress(f"Error processing JSON {file_to_process}: {str(e)}")
        return pd.DataFrame(columns=['name', 'height', 'weight'])

def extract_from_xml(file_to_process):
    try:
        dataframe = pd.DataFrame(columns=["name", "height", "weight"])
        tree = ET.parse(file_to_process)
        root = tree.getroot()
        for person in root:
            name = person.find("name").text
            height = float(person.find("height").text)
            weight = float(person.find("weight").text)
            dataframe = pd.concat([dataframe, pd.DataFrame([{"name": name, "height": height, "weight": weight}])], ignore_index=True)
        print(f"Processing XML: {file_to_process}, Data:\n{dataframe}")
        return dataframe
    except Exception as e:
        log_progress(f"Error processing XML {file_to_process}: {str(e)}")
        return pd.DataFrame(columns=['name', 'height', 'weight'])

def extract():
    extracted_data = pd.DataFrame(columns=['name', 'height', 'weight'])
    log_progress(f"Found CSV files: {glob.glob('*.csv')}")
    for csvfile in glob.glob("*.csv"):
        if csvfile != target_file:
            extracted_data = pd.concat([extracted_data, extract_from_csv(csvfile)], ignore_index=True)

    log_progress(f"Found JSON files: {glob.glob('*.json')}")
    for jsonfile in glob.glob("*.json"):
        extracted_data = pd.concat([extracted_data, extract_from_json(jsonfile)], ignore_index=True)

    log_progress(f"Found XML files: {glob.glob('*.xml')}")
    for xmlfile in glob.glob("*.xml"):
        extracted_data = pd.concat([extracted_data, extract_from_xml(xmlfile)], ignore_index=True)

    log_progress(f"Extracted Data (before transform):\n{extracted_data}")
    return extracted_data

def transform(data):
    if data.empty:
        log_progress("No data to transform")
        return data
    data = data.dropna(subset=['name', 'height', 'weight'])  # Remove rows with NaN
    data['height'] = round(data.height * 0.0254, 2)  # Inches to meters
    data['weight'] = round(data.weight * 0.45359237, 2)  # Pounds to kilograms
    log_progress(f"Transformed Data:\n{data}")
    return data

def load_data(target_file, transformed_data, db_name):
    if transformed_data.empty:
        log_progress("No data to load")
        return
    transformed_data.to_csv(target_file, index=False)
    log_progress(f"Saved to {target_file}")
    # Save to SQLite database
    try:
        conn = sqlite3.connect(db_name)
        transformed_data.to_sql('People', conn, if_exists='replace', index=False)
        log_progress(f"Saved to {db_name}, table 'People'")
        conn.close()
    except Exception as e:
        log_progress(f"Error saving to database {db_name}: {str(e)}")

# ETL Process
log_progress("ETL Job Started")
log_progress("Extract phase Started")
extracted_data = extract()
log_progress("Extract phase Ended")
log_progress("Transform phase Started")
transformed_data = transform(extracted_data)
print("Final Transformed Data:")
print(transformed_data)
log_progress("Transform phase Ended")
log_progress("Load phase Started")
load_data(target_file, transformed_data, db_name)
log_progress("Load phase Ended")
log_progress("ETL Job Ended")

# import glob
# import pandas as pd
# import xml.etree.ElementTree as ET
# from datetime import datetime

# log_file = "log_file.txt"
# target_file = "transformed_data.csv"

# def extract_from_csv(file_to_process):
#     dataframe = pd.read_csv(file_to_process)
#     return dataframe


# def extract_from_json(file_to_process):
#     dataframe = pd.read_json(file_to_process, lines=True)
#     return dataframe


# def extract_from_xml(file_to_process):
#     dataframe = pd.DataFrame(columns=["name", "height", "weight"])
#     tree = ET.parse(file_to_process)
#     root = tree.getroot()
#     for person in root:
#         name = person.find("name").text
#         height = float(person.find("height").text)
#         weight = float(person.find("weight").text)
#         dataframe = pd.concat([dataframe, pd.DataFrame([{"name":name, "height":height, "weight":weight}])], ignore_index=True)
#     return dataframe


# def extract():
#     extracted_data = pd.DataFrame(columns=['name','height','weight']) # create an empty data frame to hold extracted data

#     # process all csv files, except the target file
#     for csvfile in glob.glob("*.csv"):
#         if csvfile != target_file:  # check if the file is not the target file
#             extracted_data = pd.concat([extracted_data, pd.DataFrame(extract_from_csv(csvfile))], ignore_index=True)

#     # process all json files
#     for jsonfile in glob.glob("*.json"):
#         extracted_data = pd.concat([extracted_data, pd.DataFrame(extract_from_json(jsonfile))], ignore_index=True)

#     # process all xml files
#     for xmlfile in glob.glob("*.xml"):
#         extracted_data = pd.concat([extracted_data, pd.DataFrame(extract_from_xml(xmlfile))], ignore_index=True)

#     return extracted_data


# def transform(data):
#     '''Convert inches to meters and round off to two decimals
#     1 inch is 0.0254 meters '''
#     data['height'] = round(data.height * 0.0254,2)

#     '''Convert pounds to kilograms and round off to two decimals
#     1 pound is 0.45359237 kilograms '''
#     data['weight'] = round(data.weight * 0.45359237,2)

#     return data

# def load_data(target_file, transformed_data):
#     transformed_data.to_csv(target_file)

# def log_progress(message):
#     timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second
#     now = datetime.now() # get current timestamp
#     timestamp = now.strftime(timestamp_format)
#     with open(log_file,"a") as f:
#         f.write(timestamp + ',' + message + '\n')


# # Log the initialization of the ETL process
# log_progress("ETL Job Started")

# # Log the beginning of the Extraction process
# log_progress("Extract phase Started")
# extracted_data = extract()

# # Log the completion of the Extraction process
# log_progress("Extract phase Ended")

# # Log the beginning of the Transformation process
# log_progress("Transform phase Started")
# transformed_data = transform(extracted_data)
# print("Transformed Data")
# print(transformed_data)

# # Log the completion of the Transformation process
# log_progress("Transform phase Ended")

# # Log the beginning of the Loading process
# log_progress("Load phase Started")
# load_data(target_file,transformed_data)

# # Log the completion of the Loading process
# log_progress("Load phase Ended")

# # Log the completion of the ETL process
# log_progress("ETL Job Ended")