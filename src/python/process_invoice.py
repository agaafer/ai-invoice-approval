from pathlib import Path
import pickle
import requests
import re
import json
from wand.image import Image
from agents.ocr.claude_invoice_format_ocr import extract_text_from_image,generic_claude_function
import sys
from sklearn.metrics.pairwise import cosine_similarity
import ast
import pandas as pd
import torch.nn as nn
import torch
from transformers import DistilBertTokenizer, DistilBertModel
import numpy as np
import string
import xgboost as xgb
import xml.etree.ElementTree as ET
from scipy.spatial import distance
from fastai.tabular.all import *
torch.manual_seed(42)
def read_txt_file(file_name):
    with open(file_name,'r') as file:
        read_file = file.read()
        file.close()
        return read_file
SUPPORTED_IMG_EXTENSIONS = ['.jpeg'
'.png'
'.gif'
'.webp']
PHYSICAL_PATH = 'path'
procs=[Categorify]
baseurl = 'C:/Users/agaafer/AppData/Local/Programs/Python/Python312/Lib/imagenow/'
CLUSTER_CENTERS = baseurl +'clusterCenter1411NewData.csv'
IMAGE_LINK = 'url'
CLAUDE_OUTPUT_NAME = baseurl + 'claude_output.json'
EMBEDDINGS_MODEL_NAME = 'distilbert-base-uncased'
XML_DIRECTORY_PATH = str(Path('XML').resolve())
GL_TAGS = ['GL1', 'GL4','LocationCode']
DEFAULT_LLM_STR = "Not available"
backup_columns=['file_name', 'unit_price', 'quantity_ordered', 'total_price',
       'item_description', 'approved', 'vendor']
backup_fv = ['N/A',0,0,0,'N/A',False,'N/A']
LINE_ITEM_KEYS = ['Quantity','unit_price']
XGB_CLASSIFIER = baseurl +'finalProdModel2511.json'
FEATURES_SCALER = baseurl +'finalScalerModel3010Final.pkl'
CLUSTER_COLUMNS =['cluster_1','cluster_0']
VENDOR_LABELS = 'vendor_labels_new.csv'
VENDOR_COLUMN = 'Vendor'

VENDOR_CSV=baseurl + 'vendor_labels411.csv'
BRANCH_CSV =baseurl + 'branchLabels.csv'
gl_acc_csv = pd.read_csv(baseurl + 'gl-accounts-lookup.csv')
subacc_csv = pd.read_csv(baseurl + 'costcenter-profitcenter-lookup.csv')
COLUMNS_OF_INTEREST = ['file_name','unit_price', 'quantity_ordered', 'total_price', 'invoice_total',
    'invoice_tx', 'discountFlag', 'freightFlag', 'cluster', 'vendor_encoding', 'approved_x']
xml_columns_to_drop = ['GL1', 'GL4', 'glAcc_desc', 'costCentre_desc']
COSINE_SIMILARITY_THRESHOLD = 0.90
png_conversion = lambda x,suffix: re.sub(suffix,'',x)+'.png'
remove_parentheses = lambda str: str.replace('(','').replace(')','')
remove_comma = lambda x:x.replace(',','')
remove_currency_sign = lambda x:x.replace('$','')
check_for_str = lambda x: x if isinstance(x,str) else str(x)
binary_eval = lambda x: 1 if try_list_eval(x) else 0
flag_eval = lambda x: 1 if float(remove_comma(remove_currency_sign(str(x)))) > 0 else 0 #casting to a float to handle the case where the value is a string
shorten_name = lambda x: '_'.join(x.split('_')[:2])
get_gl_strings = lambda gl_list: gl_acc_csv[gl_acc_csv['GlAccount'].isin(gl_list)]['LongDescription'].tolist()
get_subacc_strings = lambda subacc_list: [] if type(subacc_list)!=list \
    else subacc_csv[subacc_csv['CostCentre'].isin(subacc_list)]['LongDescription'].tolist()
def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))
def write_txt_file(file_name,content):
    with open(file_name,'w') as file:
        file.write(content)

def check_list(value):
    if pd.isna(value):
        return 0
    else:
        return 1
 
def remove_xml_extension(entry):
    return entry.replace('.xml', '')

def custom_changes(df):
    df['vendor_encoding_mean'] = df['vendor_encoded_mean']
    df.drop(columns=['vendor_encoded_mean'],inplace=True) 
    
    return df

def robust_list_eval(input_list):
        if type(input_list)==list:
            return input_list
        try:
            return ast.literal_eval(input_list)
        except:
            return []

def robust_float_eval(string_val):
        try:
            return float(string_val)
        except:
            return 0
def get_gl_numbers(gl_list):
    gl_list = [int(robust_float_eval(element)) for element in gl_list]
    return gl_list
        

def encode_vendor_name(vendor_name,gt_df):
    encoding = -1
    vendor_name = preprocess_text(vendor_name)
    columns = gt_df.columns[:-1]
    all_embeddings = gt_df[columns].values
    embedding_single = get_embedding(vendor_name)
    for embedding in all_embeddings:
        expanded_arr = np.expand_dims(embedding, axis=0)
        if cosine_similarity(expanded_arr, embedding_single) > COSINE_SIMILARITY_THRESHOLD:
            mask = gt_df[columns].isin(embedding).all(axis=1)
            result = gt_df.loc[mask]
            encoding = result.index.tolist()[0] if len(result) > 0 else -1
            return encoding
        
    return encoding
        
def parse_xml_files_to_dataframe(target_file_path, gl_tags:list, other_tags:list):
    # this function is going to parse all the xml data in the directory and return a dataframe
    removing_extension = lambda x:re.sub('.xml','',x)
    rows = []
    tree = ET.parse(target_file_path)
    root = tree.getroot()
    other_data = {}
    for tag in other_tags:
        element = root.find(tag)
        other_data[tag] = element.text if element is not None else None
    
    gl_data = {tag: [] for tag in gl_tags}
    
    for gl_tag in gl_tags:
        elements = root.findall(f".//{gl_tag}")
        for element in elements:
            if element is not None and element.text is not None:
                gl_data[gl_tag].append(element.text)
    filename = Path(target_file_path).name
    row_data = {'Filename': removing_extension(filename)}
    row_data.update(other_data)
    for tag in gl_tags:
        row_data[tag] = gl_data[tag] if gl_data[tag] else None
    
    rows.append(row_data)

    df = pd.DataFrame(rows)
    return df

def preprocess_text(text):
    """Preprocess text by removing special characters and normalizing"""
    # Convert to uppercase
    text = text.upper()
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def predict_with_xgb_classifier(model_name, data):
    loaded_model = xgb.XGBClassifier()
    loaded_model.load_model(model_name)
    return loaded_model.predict(data)[0], max(list(loaded_model.predict_proba(data)[0]))

def get_model_features(model_name):
    loaded_model = xgb.XGBClassifier()
    loaded_model.load_model(model_name)
    return loaded_model.feature_names_in_

def process_xml_file(file_path):
    if Path(file_path).exists!=True:
        xml_df = parse_xml_files_to_dataframe(file_path,GL_TAGS,[])
        return xml_df
    else:
        raise Exception("XML File does not exist")

def remove_freight_from_total(invoice_dict):
    if str(invoice_dict['freight']).lower()!=DEFAULT_LLM_STR:
        invoice_dict['invoice_total'] = wrapping_preprocessing_funcs(invoice_dict['invoice_total']) - wrapping_preprocessing_funcs(invoice_dict['freight'])
# this lookup list is has its values as function signatures for now 


def handle_special_vendor_cases(invoice_dict):
    for vendor_dict in SPECIAL_VENDORS:
        vendor_name = list(vendor_dict.keys())[0]
        gt_vendor_embedding = get_embedding(vendor_name)
        extracted_vendor_embedding = get_embedding(invoice_dict['vendor'])
        if cosine_similarity(gt_vendor_embedding,extracted_vendor_embedding) > 0.9:
            vendor_dict[vendor_name](invoice_dict)

def extract_lineItems(data:tuple):
    extracted_data = []

    invoice, file_name = data
    
    if isinstance(invoice, dict):
        vendor = invoice.get('vendor', 'N/A')
        
        for item in invoice['invoice_items']:
            row = {
                'vendor': vendor,  
                'item_description': item['item_Description'],
                'unit_price': item['unit_price'],
                'quantity_ordered': item['Quantity'],
                'total_price': item['item_total'],
                'file_name': file_name,
                'approved': True
            }
            extracted_data.append(row)
    else:
        print(f"Unexpected format: {invoice}")
    return extracted_data


def extractInvoice(data:tuple):
    extracted_data = []
    invoice, file_name = data 
    
    row = {
            'invoice_total': invoice['invoice_total'],
            'invoice_tx' : invoice['invoice_tx'],
            'freight': invoice['freight'],
            'discount': invoice['discount'],
            'file_name': file_name,
            'approved': True
        }
    extracted_data.append(row)
    return extracted_data


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
    
def try_catch_wrap_json(json_data):
    try:
        json.loads(json_data)
        return True
    except:
        return False
    
def reading_pickled_models(model_name):
    with open(model_name, 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model

def json_fixing_claude_wrapper(faulty_json_output):
    json_fixing_system_prompt = """You are an expert JSON validator.
    Your excel at fixing JSON strings that are missing quotes, have unescaped quotes, or have other issues. 
    You will be given a JSON string that is missing quotes around keys and has unescaped quotes within values. 
    Your task is to fix the JSON string so that it is properly formatted and can be loaded into a Python dictionary. 
    The JSON string is stored in a variable called `json_string`.
    <HIGH PRIORITY INSTRUCTION> Please return the fixed JSON string as the final output with no extra text.</HIGH PRIORITY INSTRUCTION>"""
    user_prompt = f'json_string:{faulty_json_output}'
    try:
        content = generic_claude_function(system_prompt=json_fixing_system_prompt, user_prompt=user_prompt)
        return json.loads(content)
    except:
        return 'Invalid JSON'
    

wrapping_preprocessing_funcs = lambda strng:robust_float_eval(remove_parentheses(remove_comma(remove_currency_sign(check_for_str(strng)))))
def update_value(key,dict_):
    wrap_denominator = lambda x: 1 if int(x)==0 else x
    return_val = ''
    if key=='Quantity':
        return_val = wrapping_preprocessing_funcs(dict_['item_total'])/wrap_denominator(wrapping_preprocessing_funcs(dict_['unit_price']))
        dict_[key] = return_val
    
    elif key=='unit_price':
        return_val = wrapping_preprocessing_funcs(dict_['item_total'])/wrap_denominator(wrapping_preprocessing_funcs(dict_['Quantity']))
        dict_[key] = return_val
    return dict_[key]
    
def derive_lt_vals(invoice_dict):
    default_string = DEFAULT_LLM_STR
    smaller_list = invoice_dict['invoice_items']
    for d in smaller_list:
        for key in LINE_ITEM_KEYS:
            if str(d[key]).lower()==default_string.lower():
                d[key]= update_value(key,d)
    return invoice_dict

def validate_line_items(invoice_dict):
    invoice_items = ast.literal_eval(invoice_dict['invoice_items']) if type(invoice_dict['invoice_items'])==str else invoice_dict['invoice_items']
    for lt_dict in invoice_items:
        if lt_dict['Quantity']==DEFAULT_LLM_STR and lt_dict['unit_price']==DEFAULT_LLM_STR:
            print('The quantity and unit price are not available')
            return invoice_dict
    else:
        invoice_dict = derive_lt_vals(invoice_dict)
        return invoice_dict
    
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
    

def validating_cluster_columns(cluster_df):
    for cluster_col in CLUSTER_COLUMNS:
        if cluster_col not in list(cluster_df.columns):
            cluster_df[cluster_col] = 0


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


def get_branch_labels(data, filename):
    branch_labels = pd.read_csv(filename)
    data = data.upper()
    indices_retrieved = branch_labels.index[branch_labels["LocationCode"] == data].tolist()
    branch_encoded_label = indices_retrieved[0] if len(indices_retrieved) > 0 else -1
    return branch_encoded_label

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
    
def adapt_img_to_claude(paths):
    new_path = []
    for path_ in paths:
        file_type = Path(path_).suffix
        if file_type not in SUPPORTED_IMG_EXTENSIONS:
            adapted_img_name = convert_img_to_png(path_, png_conversion(path_,file_type))
            new_path.append(adapted_img_name)
        else:
            new_path.append(path_)
    return new_path

    
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

    df['unit_price'] = df['unit_price'].apply(clean_number)
    df['unit_price'] = abs(df['unit_price'])
    df['total_price'] = df['total_price'].apply(clean_number)
    df['total_price'] = abs(df['total_price'])
    df['quantity'] = df['quantity'].apply(clean_number)
    df['quantity'] = abs(df['quantity'])

    return df


def clean_number(price):
    def try_except_wrapper(char_seq):
        try:
            float(char_seq)
            return True
        except:
            return False  
    if isinstance(price, str):
        cleaned_price = re.sub(r'[^\d.,]', '', price)
        cleaned_price = cleaned_price.replace(',', '')
        return float(cleaned_price) if try_except_wrapper(cleaned_price)==True else 0
    elif isinstance(price, (int, float)):
        return float(price)

def clean_invoice_keys(invoice_dict,key_list):
    for key in key_list:
        if key in invoice_dict.keys():
            invoice_dict[key] = 0 if invoice_dict[key]==DEFAULT_LLM_STR else invoice_dict[key]
    return invoice_dict

def process_invoice_df(invoice_df):
    invoice_df['discountFlag'] = invoice_df['discount'].apply(clean_number)
    invoice_df['freightFlag'] = invoice_df['freight'].apply(flag_eval)
    invoice_df['unit_price'] = abs(invoice_df['unit_price'].apply(clean_number))
    invoice_df['total_price'] = abs(invoice_df['total_price'].apply(clean_number))
    invoice_df['invoice_total'] = abs(invoice_df['invoice_total'].apply(clean_number))
    invoice_df['invoice_tx'] = abs(invoice_df['invoice_tx'].apply(clean_number))
    invoice_df['quantity_ordered'] = abs(invoice_df['quantity_ordered'].apply(clean_number).astype(float))

    invoice_df['item_description'] = invoice_df['item_description'].apply(remove_punctuation)
    return invoice_df

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
    data = data.upper()
    indices_retrieved = vendor_labels.index[vendor_labels[VENDOR_COLUMN] == data].tolist()
    vendor_encoded_label = indices_retrieved[0] if len(indices_retrieved) > 0 else -1
    return vendor_encoded_label



def try_list_eval(x):
    if type(x)==list and len(x)>0:
        return True
    else:
        return None


def get_prediction(list_of_paths,xml_file_path):
    cats = ast.literal_eval(read_txt_file(baseurl +'cat_columns.txt'))
    conts = ast.literal_eval(read_txt_file(baseurl +'cont_columns.txt'))
    scale_rf_vals = lambda df: TabularPandas(df,procs=procs,cat_names=cats,cont_names=conts,splits=None,reduce_memory=False).xs
    gl_description = 'glAcc_desc'
    subacc_description = 'costCentre_desc'
    #file_desc=extracted_tuple[1]
    #claude_output = extracted_tuple[0]
    file_desc = Path(list_of_paths[0]).name
    xmlData = process_xml_file(xml_file_path)
    xmlData['GL1'] = xmlData['GL1'].apply(robust_list_eval)
    xmlData['GL4'] = xmlData['GL4'].apply(robust_list_eval)
    xmlData[gl_description] = xmlData['GL1'].apply(get_gl_numbers).apply(get_gl_strings)
    xmlData[subacc_description] = xmlData['GL4'].apply(get_subacc_strings)
    xmlData['gl_invoice_count'] = xmlData['GL1'].apply(lambda x: len(x))
    xmlData['gl_actual_count'] = xmlData[gl_description].apply(lambda x: len(x))
    xmlData['subacc_invoice_count'] = xmlData['GL1'].apply(lambda x: len(x))
    xmlData['subacc_actual_count'] = xmlData[subacc_description].apply(lambda x: len(x))
    xmlData = xmlData.drop(xml_columns_to_drop, axis=1)
    files = adapt_img_to_claude(list_of_paths)
    claude_output = extract_text_from_image(files)
    claude_output = validate_line_items(claude_output)
    cleaned_claude_output = clean_invoice_keys(claude_output, ['discount', 'freight'])
    write_json_file(file_name=CLAUDE_OUTPUT_NAME,content= cleaned_claude_output)
    extracted_file_tuple = (cleaned_claude_output, shorten_name(file_desc))
    lineItems = pd.DataFrame(extract_lineItems(extracted_file_tuple))
    if lineItems.shape[0]==0:
        lineItems = pd.DataFrame([backup_fv],columns=backup_columns)
        lineItems['file_name'] = extracted_file_tuple[1]
    lineItems.to_csv('line_items_example.csv',index=False)
    invoiceData = pd.DataFrame(extractInvoice(extracted_file_tuple))
    invoices = pd.merge(invoiceData, lineItems, on='file_name')
    invoices = process_invoice_df(invoices)
    keeps_description = ['item_description']
    descriptions = invoices[keeps_description]
    invoices = invoices.drop(['discount', 'freight'], axis=1)
    embeddings = np.array([get_embedding(text) for text in descriptions['item_description']])
    embeddings = embeddings.reshape(embeddings.shape[0], 768)
    clustersLabels = []
    for i in range(embeddings.shape[0]):
        labels = get_labels(embeddings[i],CLUSTER_CENTERS)
        clustersLabels.append(labels)
    invoices.drop(['item_description','approved_y'], axis=1, inplace=True)
    invoices.reset_index(drop=True, inplace=True)
    single_vendor = invoices['vendor'][0]
    vendor_encoded = encode_vendor_name(single_vendor,pd.read_csv(VENDOR_CSV))
    branch_name = xmlData['LocationCode'].tolist()[0][0]
    branch_index = get_branch_labels(branch_name,BRANCH_CSV)
    invoices['LocationCode'] = int(branch_index)
    xmlData.drop(['LocationCode'],axis=1,inplace=True) 

    invoices['vendor_encoding'] = vendor_encoded
    invoices['cluster'] = clustersLabels

    lineItems = invoices[COLUMNS_OF_INTEREST]
    statisticsTrain = lineItems.groupby('file_name').agg({
        'unit_price': ['min', 'max', 'mean', 'sum'],
        'quantity_ordered': ['min', 'max', 'mean', 'sum'],
        'total_price': ['min', 'max', 'mean', 'sum'],
        'approved_x': ['mean'],
        'file_name': ['count'],
        'vendor_encoding': ['mean'],
        'discountFlag': ['mean'],
        'freightFlag': ['mean'],
        'invoice_total': ['mean'],
        'invoice_tx': ['mean']
    }).reset_index()

    statisticsTrain.columns = ['_'.join(col).strip() if col[1] else col[0] for col in statisticsTrain.columns.values]

    cluster_train = lineItems.groupby(['file_name', 'cluster']).size().unstack(fill_value=0).reset_index()
    cluster_train.columns = ['file_name'] + [f'cluster_{col}' for col in cluster_train.columns[1:]]
    validating_cluster_columns(cluster_train)
    finalTrain = pd.merge(statisticsTrain, cluster_train, on='file_name')
    xmlData['file_name'] = xmlData['Filename'].apply(remove_xml_extension)
    xmlData.drop(['Filename'], axis=1, inplace=True)
    finalTrain['LocationCode']= branch_index 
    finalTrain = pd.merge(finalTrain, xmlData, on='file_name')
    
    X = finalTrain.drop(["approved_x_mean"], axis = 1)
    X.drop(['file_name'], axis=1, inplace=True)
 
    # X = custom_changes(X)
    processed_features =X.copy()
 
    processed_features.to_csv("final_feature_vector.csv",index=False)
    if processed_features['gl_invoice_count'].tolist()[0]==0 and processed_features['subacc_actual_count'].tolist()[0]==0:
        pred,probability=1,0.90
        print('no_gl and subacc')
    else:
        pred,probability = predict_with_xgb_classifier(XGB_CLASSIFIER,processed_features[get_model_features(XGB_CLASSIFIER)])
        
    output_dict = {"predicted_class":int(pred),'predicted_probability':float(probability)}
    enclosing_json = {"ml_output":output_dict    , "invoice":claude_output}
    
    return  enclosing_json if try_catch_wrap_json(enclosing_json)==True else {"prediction":output_dict    \
            , "invoice":json_fixing_claude_wrapper(claude_output)}


# functions end
SPECIAL_VENDORS = [{'Canature WaterGroup Canada Inc.':remove_freight_from_total}]