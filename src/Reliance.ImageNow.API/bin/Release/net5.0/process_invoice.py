from pathlib import Path
import pickle
import requests
import re
import json
from wand.image import Image
from agents.ocr.claude_invoice_format_ocr import extract_text_from_image
import sys
import ast
import pandas as pd

import torch
from transformers import DistilBertTokenizer, DistilBertModel
import numpy as np
import string
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

from scipy.spatial import distance


SUPPORTED_IMG_EXTENSIONS = ['.jpeg'
'.png'
'.gif'
'.webp']

PHYSICAL_PATH = 'path'
IMAGE_LINK = 'url'
CLAUDE_OUTPUT_NAME = 'claude_output.json'
EMBEDDINGS_MODEL_NAME = 'distilbert-base-uncased'

tokenizer = DistilBertTokenizer.from_pretrained(EMBEDDINGS_MODEL_NAME)
model = DistilBertModel.from_pretrained(EMBEDDINGS_MODEL_NAME)

png_conversion = lambda x,suffix: re.sub(suffix,'',x)+'.png'

def save_image(image_string):
    string_type = check_string_type(image_string)
    if string_type == PHYSICAL_PATH:
        file_name = str(Path(image_string).resolve())
    elif string_type == IMAGE_LINK:
        file_name = download_image(image_string)

    return file_name

def check_string_type(s):
    # Regular expression for URLs
    url_pattern = re.compile(r'^(http://|https://|www\.)')
    
    # Check if the string matches the URL pattern
    if url_pattern.match(s):
        return 'url'
    else:
    # assume it is a path string
        return 'path'
    
def reading_pickled_models(model_name):
    with open(model_name, 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model
    
def extract_extension(content_type:str)->str:
    pattern = r'/([^/]*)$'
    EXT_PREFIX = '.'
    extension = ''
    match = re.search(pattern, content_type)
    if match:
        result = match.group(1)
        extension = EXT_PREFIX + result
        return extension
    else:
        # this implementation is tightly coupled to the response type attribute of the requests object, that will be changed later
        # assuming that the content type did not have the / character and it returned the extension of the file right away
        return  EXT_PREFIX+extension
    
def download_image(img_url:str):
    # Send a GET request to the URL
    response = requests.get(img_url)
    # Check if the request was successful
    if response.status_code == 200:
        # Get the content type from the headers
        content_type = response.headers.get('content-type')
        extension =  extract_extension(content_type)
        full_path = 'image'+extension
        with open(full_path, 'wb') as file:
            file.write(response.content)
    return full_path

def convert_img_to_png(input_path, output_path):
    try:
        with Image(filename=input_path) as img:
            # Convert the image to PNG format
            img.format = 'png'
            # Save the image
            img.save(filename=output_path)
        
        print(f"Successful conversion")
        return output_path
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return input_path
    
def adapt_img_to_claude(file_name):
    file_type = Path(file_name).suffix
    if file_type not in SUPPORTED_IMG_EXTENSIONS:
        adapted_img_name = convert_img_to_png(file_name, png_conversion(file_name,file_type))
        return adapted_img_name
    else:
        return file_name
    
def write_json_file(file_name,content):
    with open(file_name,'w') as file:
        json.dump(content,file)

def extract_data(data:tuple) -> list:
    extracted_data = []

    invoice, file_name = data
    
    if isinstance(invoice, dict):
        vendor = invoice.get('vendor', 'N/A')
        
        for item in invoice['invoice_items']:
            row = {
                'vendor': vendor,  
                'item_description': item['item_Description'],
                'unit_price': item['unit_price'],
                'quantity': item['Quantity'],
                'total_price': item['item_total'],
                'file_name': file_name
            }
            extracted_data.append(row)
    else:
        print(f"Unexpected format: {invoice}")

    return extracted_data

def convert_list_to_df(list_of_dicts:list) -> pd.DataFrame:
    df = pd.DataFrame(list_of_dicts)

    df['unit_price'] = df['unit_price'].apply(clean_price)
    df['unit_price'] = abs(df['unit_price'])
    df['total_price'] = df['total_price'].apply(clean_price)
    df['total_price'] = abs(df['total_price'])
    df['quantity'] = df['quantity'].astype(float)
    df['quantity'] = abs(df['quantity'])

    return df


def clean_price(price):
    if isinstance(price, str):
        cleaned_price = re.sub(r'[^\d.,]', '', price)
        return float(cleaned_price.replace(',', ''))
    elif isinstance(price, (int, float)):
        return float(price)
    return np.nan

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def get_embedding(text):
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    
    model = DistilBertModel.from_pretrained('distilbert-base-uncased')
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

def get_labels(data, filename):
    cluster_centers = pd.read_csv(filename)
    cluster1 = cluster_centers[cluster_centers.columns[0]].values
    cluster2 = cluster_centers[cluster_centers.columns[1]].values

    distance1 = distance.euclidean(cluster1, data)
    distance2 = distance.euclidean(cluster2, data)

    if distance1 < distance2:
        return 0
    else:
        return 1
    
def get_vendor_labels(data, filename):
    vendor_labels = pd.read_csv(filename)

    vendor_encoded_label = vendor_labels.index[vendor_labels['vendor'] == data].tolist()[0]

    return vendor_encoded_label

def get_xgboost_prediction(X_array, model):
    loaded_model = xgb.Booster() 
    loaded_model.load_model(model)

    dtest = xgb.DMatrix(X_array)

    y_pred = loaded_model.predict(dtest)

    return y_pred


def get_perdiction(f):
    #file_name = download_image(img_url = sys.argv[1])
    file_name = f
    file = adapt_img_to_claude(file_name)
    claude_output = extract_text_from_image(file)
    write_json_file(file_name=CLAUDE_OUTPUT_NAME,content= claude_output)
    extracted_file_tuple = (claude_output, file)
    extracted_data = extract_data(extracted_file_tuple)
    data = convert_list_to_df(extracted_data) 
    descriptions = data.drop(['vendor','unit_price','quantity','total_price'], axis = 1)

    

    embeddings = np.array([get_embedding(text) for text in descriptions['item_description']])

    embeddings = embeddings.reshape(embeddings.shape[0], 768)

    labels = []

    for i in range(embeddings.shape[0]):
        labels.append(get_labels(embeddings[i], 'clusters.csv'))
    labels_df = pd.DataFrame(labels, columns=['cluster'])

    embeddings_df = pd.DataFrame(embeddings, columns=[f'embedding_{i}' for i in range(embeddings.shape[1])])

    finalDf = pd.concat([data, embeddings_df], axis=1)
    single_value = finalDf['vendor'].tolist()[0]
    vendor_label = get_vendor_labels(single_value, 'vendor_labels.csv')
    finalDf = pd.concat([data, embeddings_df], axis=1)
    single_value_vendor = finalDf['vendor'].tolist()[0]
    vendor_label = get_vendor_labels(single_value_vendor, 'vendor_labels.csv')
    finalDf['vendor_encoded'] = vendor_label
    finalDf = pd.concat([finalDf, labels_df], axis=1)
    finalDf = finalDf.drop(['item_description', 'vendor'], axis = 1)

    X = finalDf.drop(['file_name'], axis = 1)
    first_scaler = reading_pickled_models('scaler_object_lineItems.pkl')
    ordered_scaled_df = X[list(first_scaler.feature_names_in_)]
    X_scaled = first_scaler.transform(ordered_scaled_df)
    old_order = X.columns.tolist()
    # reversed_scaled_df = X_scaled[old_order]
    line_Items_Prediction = get_xgboost_prediction(X_scaled, 'lineItems.json')

    finalDf['predicted'] = line_Items_Prediction
    predicted = finalDf.groupby('file_name')['predicted'].mean().reset_index()
    statistics = finalDf.groupby('file_name').agg({
    'unit_price': ['mean', 'sum', 'min', 'max'],
    'quantity': ['mean', 'sum', 'min', 'max'],
    'total_price': ['mean', 'sum', 'min', 'max'],
    'file_name': ['count']
})

    statistics.columns = ['_'.join(col) if col[1] != '' else col[0] for col in statistics.columns]

    statistics.reset_index(inplace=True)

    finalDf = pd.merge(statistics, predicted, on='file_name')

    X = finalDf.drop(['file_name'], axis = 1)
    second_scaler = reading_pickled_models('scaler_object_invoices.pkl')
    ordered_df = X[list(second_scaler.feature_names_in_)]
    X_scaled = second_scaler.transform(ordered_df)
    # reverse_ordered_df = X_scaled[X.columns.tolist()]
    invoices_Prediction = get_xgboost_prediction(X_scaled, 'invoices.json')
    single_prediction = list(invoices_Prediction)[0]

    output_df = pd.DataFrame(data=invoices_Prediction, columns=['probability'])
    print(output_df.to_json())
    output_json = json.loads(output_df.to_json())['probability']
    
    return {"prediction":output_json    , "invoice":claude_output}
    