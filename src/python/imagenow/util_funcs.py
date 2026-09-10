import os
import fitz
from openai import AzureOpenAI
import ast
import base64
import json
from collections import Counter
import re
from PIL import Image
import pytesseract
import pandas as pd

import matplotlib.pyplot as plt
from agents.ocr.claude_invoice_format_ocr import extract_text_from_image
from datetime import timedelta
# vision_client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_KEY_VISION"),
#                      api_version="2023-05-15",
#                      azure_endpoint =os.getenv("AZURE_OPENAI_ENDPOINT_VSION"))

# client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_KEY"),
#                      api_version="2023-05-15",
#                      azure_endpoint =os.getenv("AZURE_OPENAI_ENDPOINT"))
vision_client = dict()
client = dict()


zip_folders = lambda x,y: list(zip(x,y))
PANDAS_DATETYPE = pd._libs.tslibs.timestamps.Timestamp
get_invoice_names = lambda list: [file for file in os.listdir(list)]
get_invoice_paths = lambda directory,file_list: [os.path.join(directory,file) for file in file_list]
get_first_elements = lambda list_:[element[0] for element in list_]
getting_samples = lambda list_,upper_bound,lower_bound: [element \
                 for element in list_ \
if int(element[list(element.keys())[0]]) < upper_bound and \
int(element[list(element.keys())[0]]) > lower_bound ]
get_last_elements = lambda list_:[element[-1] for element in list_]
sublisting = lambda list_,indices: [list_[index] for index in indices]
print_len = lambda list_: print(len(list_)) 
eval_list_json = lambda list_: [json.loads(element) for element in list_]
element_transform = lambda list: ['_'.join(element.split('_')[:2]) for element in list]
shorten_name = lambda x: '_'.join(x.split('_')[:2])



def encode_image(image_path):
    with open(image_path,"rb") as image_file:
        return  base64.b64encode(image_file.read()).decode("utf-8")

def filter_with_indices(target_list,falsy_indices):
    """Returns a list of elements that are not in the falsy_indices list."""
    return [target_list[index] for index in range(len(target_list)) if index not in falsy_indices]

def convert_names_to_paths(list_names:list,directory):
    """Returns a list of file paths from a list of file names."""
    return [os.path.join(directory,name) for name in list_names]


def apply_OCR(image_path):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    img = Image.open(image_path)
    image_text = pytesseract.image_to_string(img)
    return image_text

def escape_internal_dir_path(dir_name):
    dir_name = '\\'+dir_name
    unescaped_path = os.getcwd() + dir_name
    return unescaped_path.encode('unicode_escape').decode()

def create_new_dir(dirname):
    
    new_dir  = escape_internal_dir_path(dirname)

    os.mkdir(new_dir)
    return new_dir

def get_invoice_template(template_txt_file:str):
    another_path = escape_internal_dir_path('templates')
    with open(os.path.join(another_path, template_txt_file), 'r') as text_file:
            internalPO = text_file.read()
            output_template_line_item  = internalPO
    return output_template_line_item

def move_files_to_dir_extension(dirname,file_extension):
    new_path = create_new_dir(dirname)
    current_files = os.listdir(os.getcwd())
    files_to_move = [file for file in current_files if file.endswith(file_extension)]
    [os.rename(file,os.path.join(new_path,file)) for file in  files_to_move]

def move_files_to_dir(dirname,old_dir,file_names:list):
    """Moves files from one directory to another."""
    new_path = create_new_dir(dirname)
    [os.rename(os.path.join(old_dir,file_name),os.path.join(new_path,file_name)) for file_name in file_names]



def fix_json_error(faulty_json):
    messages = [{"role": "system",
                "content": "You are a data structure validator. Your task is to correct and validate several data structures."},
                {"role": "user", "content":f"Validate this JSON object and fix it based on the standard syntactic JSON rules, the faulty JSON: {faulty_json}"}]

    completion = client.chat.completions.create(
    model="gpt-4",
    response_format={"type":"json_object"},
    max_tokens=1000,
    messages=messages,)

    response = completion.choices[0].message.content
    return response

def count_missing_vals(initial_template):
    all_vals = sum([ float(True) for value in list(initial_template.values()) if value!=''])
    if all_vals<len(list(initial_template.values())):
        return True
    else:    
        return False
    

def generate_missing_line_items(ground_truth_count,wrong_count,encoded_image,faulty_template):
    output_template = """"{
				"description":"",
				"unit_price":"",
				"quantity_ordered":"",
				"total_price":""
				}"""
    messages = [{"role": "system", "content": """You are a procurement analyst with a very sharp eye for detail.
                  Your task is to validate extracted information from invoices and fill in any missing values."""},
                {"role": "user","content":
                [{"type":"text","text":"""###Read through the entire invoice first and then read the extracted template."""+
                  f"""###Validate your output against the following rules:
                  - The actual count of line items is: {ground_truth_count}, whereas the the count of the extracted items are: {wrong_count}. Check for any missing line items that could explain that mismatch.
                    - Return the missing line items only
                    - Lastly, return your output as JSON, based on this template = {output_template} .
                    The extracted template:{faulty_template}"""}
                  ,{"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded_image}"}}]}]

    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type":"json_object"},
    max_tokens=4000,
    messages=messages,)

    response = completion.choices[0].message.content
    try:response = ast.literal_eval(response)
    except:print("not json")
    return response

def fill_invoice_data(encoded_image,faulty_template):
    messages = [{"role": "system", "content": """You are a procurement analyst with a very sharp eye for detail.
                  Your task is to validate extracted information from invoices and fill in any missing values."""},
                {"role": "user","content":
                [{"type":"text","text":"""###Read through the entire invoice first and then read the extracted template.
                   ###If you encounter any missing value for any key in the template, please fill it based on the information that you can find in the invoice itself."""
                  f"""###P.S.: Validate your output against the following rules:
                    - If any field in the invoice contained a number in the field's key,
                      ignore that number and return the value of that key.
                    For example: 'Freight 10: 19'.
                    - Return your output as JSON, just like the template that you will validate. 
                    - If the invoice does not explicitly state the total amount, you can calculate it by summing the line items' prices.
                    The extracted template:{faulty_template}
                    - Lastly, if the missing fields in the template are not found in the invoice, just return an empty string in the field's value."""}
                  ,{"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded_image}"}}]}]

    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type":"json_object"},
    max_tokens=4000,
    messages=messages,)

    response = completion.choices[0].message.content
    return response

# The evolution of this function is that it will take a file name that will be used to fetch the correct image file for the invoice that will be filled.
def recursive_completion(target_image,json_string,counter=3):
    try:
        corrected_skeleton = json.loads(json_string)
    except:
        corrected_skeleton = fix_json_error(json_string)
        try:
            corrected_skeleton = json.loads(corrected_skeleton)
        except:
            return ""
    for i in range(counter):
        corrected_skeleton = json.loads(corrected_skeleton) if type(corrected_skeleton)==str else corrected_skeleton
        if count_missing_vals(corrected_skeleton)==False:
            return corrected_skeleton
        elif i==counter:
            return corrected_skeleton
        else:
            missing_kv = fill_invoice_data(encode_image(target_image),corrected_skeleton)
            missing_kv = json.loads(missing_kv)
            corrected_skeleton.update(missing_kv)


def chat_with_turbo_procurement(user_defined_prompt):
    messages = [{"role": "system", "content": "You are a procurement analyst. Your task is to extract the information from invoices, based on user-defined criteria."}
                ,{"role": "user", "content":user_defined_prompt }]
    completion = client.chat.completions.create(
    model="gpt-4",
    response_format={"type":"json_object"},
    max_tokens=1000,
    messages=messages)
    response = completion.choices[0].message.content
    return response



def get_lt_count(encoded_image):
    output_template = "{'purchased_items':<count_of_line_items>}"
    messages = [{"role": "system", "content": """You are a very skilled procurement analyst with a sharp eye for detail.
                  Your task is to extract information from an invoice."""},
                {"role": "user", "content":
                [{"type":"text","text":"""###Read carefully through the entire invoice,
                   so that you can extract certain information from it.
                  ###Your task is to count the number of purchased items found in the invoice."""
                  f"""#P.S.: Validate your output against the following rules:
                    - Return the count of purchased items as an integer.
                    - Return your output as JSON based on the following template:{output_template}
                    """}
                  ,{"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded_image}"}}]}]

    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type":"json_object"},
    max_tokens=100,
    messages=messages,)

    response = completion.choices[0].message.content
    return response

def extract_invoice_data(encoded_image,invoice_skeleton_outline=''):
    messages = [{"role": "system", "content": """You are a very skilled procurement analyst with a sharp eye for detail.
                  Your task is to extract the text from an invoice."""},
                {"role": "user", "content":
                [{"type":"text","text":"""#Read carefully through the entire invoice,
                   so that you can extract certain information from it."""
                  f"""#P.S.: Validate your output against the following rules:
                    - If any field in the invoice contained a number in the field's key,
                      ignore that number and return the value of that key.
                    For example: 'Freight 10: 19'.
                    - Return your output as JSON based on the following template:{invoice_skeleton_outline}
                    """}
                  ,{"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded_image}"}}]}]

    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type":"json_object"},
    max_tokens=4000,
    messages=messages,)

    response = completion.choices[0].message.content
    return response


def extract_line_items(encoded_image,optional_prompt=''):
    output_template_line_item = get_invoice_template('line_item_template.txt')
    messages = [{"role": "system", "content": """You are an image interpreter.
                  Your task is to extract the text from an invoice."""},
                {"role": "user", "content":
                [{"type":"text","text":"""#Read through the entire invoice and extract the line items found in the invoice."""+optional_prompt+
                  f"""#P.S.: Validate your output against the following rules:
                    - If any field in the invoice contained a number in the field's key,
                      ignore that number and return the value of that key.
                    For example: 'Freight 10: 19'.
                    - Return your output as JSON based on the following template:[{output_template_line_item}]"""}
                  ,{"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded_image}"}}]}]

    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type":"json_object"},
    max_tokens=4000,
    messages=messages,)

    response = completion.choices[0].message.content
    return response



def get_line_item_count_dir(target_dir:str,img_files:list):
    line_item_list = []
    txt_dir_string = target_dir
    invoice_skeletons_dir = escape_internal_dir_path(txt_dir_string)
    invoice_skeletons = os.listdir(invoice_skeletons_dir)
    for index,file in enumerate(invoice_skeletons):
        with open(os.path.join(invoice_skeletons_dir,file),'r') as file_path:
            input = file_path.read()
            text = json.loads(input) if type(input)==str else input
            text = {k.capitalize():v for k,v in text.items()}
            line_item_list.append({img_files[index].split('.')[0]:text["Line_item_count"]})
    return line_item_list        


def count_line_items(line_items_batch,img_files):
    count_dicts=[]
    for index,invoice in enumerate(line_items_batch):
        invoice_key = img_files[index].split(".")[0]
        invoice_dict = {invoice_key:""}
        count =len(line_items_batch[index]['line_item_table'])
        invoice_dict[invoice_key] = count
        count_dicts.append(invoice_dict)
    return count_dicts
    
def validate_line_item_count(normal_line_items,ground_truth,img_files):
    invoice_dump = []
    count_dicts = []
    for index,invoice in enumerate(normal_line_items):
        invoice_key = img_files[index].split(".")[0]
        invoice_dict = {invoice_key:""}
        count =len(normal_line_items[index]['line_item_table'])
        invoice_dict[invoice_key] = count
        count_dicts.append(invoice_dict)
    
    for derived_count_dict,ground_truth in zip(count_dicts,ground_truth):
        derived_dict_key = list(derived_count_dict.keys())[0]
        ground_truth_key = list(ground_truth.keys())[0]
        if derived_count_dict[derived_dict_key]!=ground_truth[ground_truth_key]:
            invoice_dump.append({ground_truth_key:derived_count_dict[derived_dict_key]})
    return invoice_dump



def invoice_skeleton_validation(invoice_skeleton_paths_list,img_files):
    for index,invoice_skeleton in enumerate(invoice_skeleton_paths_list):
        
        with open(invoice_skeleton,'r') as file:
            initial_template = str(file.read())
        print(index)
        corrected_skeleton = recursive_completion(img_files[index],initial_template)

        with open(invoice_skeleton,'w') as file:
            file.write(str(corrected_skeleton))


def calculate_totals(normal_line_items,img_files):
    totals_dicts = []
    for index,invoice in enumerate(normal_line_items):
        totals = 0
        invoice_key = img_files[index].split(".")[0]
        invoice_dict = {invoice_key:""}
        for item_no in range(len(normal_line_items[index]['Line_item_table'])):

            totals+=float(normal_line_items[index]['Line_item_table'][item_no]['total_price'])
        invoice_dict[invoice_key] = totals
        totals_dicts.append(invoice_dict)
    return totals_dicts


def get_invoice_template(template_txt_file:str):
    another_path = escape_internal_dir_path('templates')
    with open(os.path.join(another_path, template_txt_file), 'r') as text_file:
            internalPO = text_file.read()
            output_template_line_item  = internalPO
    return output_template_line_item

def validate_single_call(faulty_json,recursion_counter=0):
    if recursion_counter == 3:
        return ""
    response=""
    try:
        response = json.loads(fix_json_error(faulty_json))
        return response
    except json.JSONDecodeError:
            recursion_counter+=1
            validate_single_call(faulty_json,recursion_counter)

    return response

def count_lacking_invoices(invoices):
    count_nulls = 0
    for invoice in invoices:
        if count_missing_vals(invoice) == True:
            count_nulls+=1
    return count_nulls

def type_cast_print_error(list):
    output_lst = []
    faulty_invoices = []
    count=-1
    for dictionary,invoice_name in list:
        count+=1
        try:
            element_dict = ast.literal_eval(dictionary)
            output_lst.append(element_dict)
        except:
            faulty_invoices.append(count)
    return output_lst,faulty_invoices

def get_imgs_from_root():
    return [file for file in os.listdir(os.getcwd()) if file.endswith('.png')]

def get_dir_content(dir_name):
    return [file for file in os.listdir(dir_name)]


def read_txt_file(file_name):
    with open(file_name,'r') as file:
        read_file = file.read()
        file.close()
        return read_file
    
def write_txt_file(file_name,content):
    with open(file_name,'w') as file:
        file.write(content)


def get_line_item_count(invoice_skeletons,img_files):
    line_item_list = []
    for index,skeleton in enumerate(invoice_skeletons):

        text = json.loads(skeleton) if type(input)==str else skeleton
        text = {k.capitalize():v for k,v in text.items()}
        line_item_list.append({img_files[index].split('.')[0]:text["Line_item_count"]})
    return line_item_list  



def read_json_file(file_name):
    with open(file_name,'r',encoding='latin-1') as file:
        return json.load(file)
    
def filter_invoices(invoices_list:list,invoice_names:list,lookup_term_list:list,key_filter:bool):
    wolsley_invoices = []
    wolsley_invoice_names = []
    key_filter=False
    for index,invoice in enumerate(invoices_list):
        if key_filter==True:
            search_terms = list(invoice.keys())
        else:
            search_terms = list(invoice.values())
        if any(term in search_terms for term in lookup_term_list):
            wolsley_invoices.append(invoice)
            wolsley_invoice_names.append(invoice_names[index])
    return wolsley_invoices,wolsley_invoice_names


def complete_invoice_data(encoded_image,missing_fields:list):
    output_template = "{'<first_missing_field>':'<value>','<second_missing_field>':'<value>',...}"
    messages = [{"role": "system", "content": """You are a procurement analyst with a very sharp eye for detail.
                  You will be asked to find values for a list of missing fields."""},
                {"role": "user","content":
                [{"type":"text","text":"""###Read through the entire invoice first and then look for the missing fields.
                   ### Scan the invoice for the values of the missing fields and fill them in."""
                  f"""###P.S.: Validate your output against the following rules:
                    - If any field in the invoice contained a number in the field's key,
                      ignore that number and return the value of that key.
                    For example: 'Freight 10: 19'.
                    - Return your output as JSON, unpack each element in the missing fields list into a key value pair
                     and return JSON containing key value pairs for fields that have values in the invoice, i.e.,{output_template}
                    .
                    The missing values are:{missing_fields}
                    - Lastly, if the missing fields in the template are not found in the invoice, just return an empty string in the field's value."""}
                  ,{"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded_image}"}}]}]

    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type":"json_object"},
    max_tokens=1000,
    messages=messages,)

    response = completion.choices[0].message.content
    return response


def return_missing_fields(sample_dict:dict):
    lookup_errors = ['','None','null',None]
    missing_keys=[]
    for k,v in sample_dict.items():
        if v in lookup_errors:
            missing_keys.append(k)
    return missing_keys 

def recursive_field_completion(invoice_metadata,invoice_image,recursion_counter=3):
    missing_fields = return_missing_fields(invoice_metadata)
    if len(missing_fields)>0 and recursion_counter>0:
        try:
            gpt_completion = complete_invoice_data(encode_image(invoice_image),missing_fields)
        except Exception as e:
            print(e)
            return invoice_metadata
        invoice_metadata.update(json.loads(gpt_completion))
        return recursive_field_completion(invoice_metadata,invoice_image,recursion_counter-1)
    else:

        return invoice_metadata
    

def validate_list(list_of_elements: list, validation_function: callable, *args, **kwargs):
    fallen_indices = []
    for index, element in enumerate(list_of_elements):
        if validation_function(element, *args, **kwargs):
            continue
        else:
            fallen_indices.append(index)
    return fallen_indices


def compare_lt_count(short_list,corrected_lt_gt):
    """Returns the ground truth line item counts that do not match the derived line item counts."""
    invoice_dump = []
    for derived_count_dict,ground_truth in zip(short_list,corrected_lt_gt):
            derived_dict_key = list(derived_count_dict.keys())[0]
            ground_truth_key = list(ground_truth.keys())[0]
            if derived_count_dict[derived_dict_key]!=ground_truth[ground_truth_key]:
                invoice_dump.append({ground_truth_key:derived_count_dict[derived_dict_key]})
    return invoice_dump

def get_root_dir_path():
    current_dir_path = os.getcwd()
    return os.path.abspath(current_dir_path)


def test_overlap(first_list,second_list):
    overlap = set(first_list) & set(second_list)
    print(len(overlap))
    return list(overlap)


def find_mode(strings):
    # Create a Counter object to count the frequencies of elements in the list
    counter = Counter(strings)
    # Find the string with the highest frequency
    mode_data = counter.most_common(1)  # most_common(1) returns a list of the top 1 most common elements
    
    if mode_data:
        mode_string, count = mode_data[0]
        confidence_score = count / len(strings)
        return mode_string
    else:
        return None
    

def replacing_substrings(strings_list,old_substring,new_substring): 
    """Replacing a substring from the strings in a list of strings"""
    return [re.sub(old_substring,new_substring,string) for string in strings_list]
def replacing_keys(dict_list,new_key_list):
    """Replacing a key from a dictionary"""
    return [{new_key:list(dict.values())[0]} for new_key,dict in zip(new_key_list,dict_list)]

def get_dict_keys(list_of_dicts):
    """Getting the keys of a list of dictionaries"""
    return [list(dict.keys())[0] if len(list(dict.keys()))==1  else list(dict.keys()) for dict in list_of_dicts]
def get_dict_values(list_of_dicts):
    """Getting the values of a list of dictionaries"""
    return [{list(dict.values())[0]} if len(list(dict.values()))==1  else list(dict.values()) for dict in list_of_dicts]


def chat_with_4o(user_defined_prompt,encoded_image):
    messages = [{"role": "system", "content": "You are a procurement analyst. Your task is to extract the information from invoices, based on user-defined criteria."}
                ,{"role": "user", "content":[{"type":"text","text":user_defined_prompt},{"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded_image}"}}]}]
                
    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type":"json_object"},
    max_tokens=4000,
    messages=messages)
    response = completion.choices[0].message.content
    return response

def validate_line_item_total(line_items,financial_summary):
    remove_parentheses = lambda str: str.replace('(','').replace(')','')
    remove_comma = lambda x:x.replace(',','')
    remove_currency_sign = lambda x:x.replace('$','')
    check_for_null = lambda x: 0 if x =='' else x
    check_for_str = lambda x: x if isinstance(x,str) else str(x)
    derived_total = 0
    if type(line_items['line_item_table']) == list:
        for dict_ in line_items['line_item_table']:
            dict_['unit_price'] = float(check_for_null(remove_comma(remove_currency_sign(check_for_str(dict_['unit_price'])))))
            dict_['quantity_ordered'] = int(float(check_for_null(remove_comma(check_for_str(dict_['quantity_ordered']))))) 
            dict_['total_price'] = round(float(check_for_null(remove_comma(remove_currency_sign(check_for_str(dict_['total_price']))))),2)
            derived_total += dict_['total_price']
    elif type(line_items['line_item_table']) == dict:
        line_items['line_item_table']['unit_price'] = float(check_for_null(remove_comma(remove_currency_sign(check_for_str(line_items['line_item_table']['unit_price']))))) 
        line_items['line_item_table']['quantity_ordered'] = int(float(check_for_null(remove_comma(check_for_str(line_items['line_item_table']['quantity_ordered']))))) 
        derived_total = round(float(remove_comma(remove_currency_sign(check_for_str(line_items['line_item_table']['total_price'])))),2) 

    actual_total = round(float(check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(financial_summary['total'])))))),2) 
    actual_tax = round(float(check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(financial_summary['hst'])))))),2) 
    if round(derived_total + actual_tax,2) == actual_total:
        return True
    else:
        return False
    
def correct_dict_key(x:dict):
# this function changes the line item dictionary in place.
    if 'line_item_table' in x.keys():
        return x
    else:
        line_items = x[list(x.keys())[0]]
        x['line_item_table'] = line_items
        del x[list(x.keys())[0]]
        return x
    

def fix_line_item_keys(line_items,
            keys_list=["description",
			 "unit_price",
			 "quantity_ordered",
			 "total_price"]):
    fix_keys_prompt = """You are going to receive a list of dictionaries that contain erroneous keys.
    
    Your task is to fix those keys by replacing them with the correct keys.
    
    The correct keys are as follows:{}
    The dictionaries are as follows:{}
    ### Take care to remove any extra keys and make sure that each dictionary has only the keys specfied in the ground truth keys list.
    ### Return your output as a valid JSON."""
    for line_item in line_items:
        items = line_item['line_item_table']
        all_keys = get_dict_keys(items)
        unduplicated_keys = list(set([key for sublist in all_keys for key in sublist]))
        irregular_keys  = True if sum([float(True) for key in unduplicated_keys if key not in keys_list])>0 else False
        if irregular_keys:
            corrected_line_item = chat_with_turbo_procurement(fix_keys_prompt.format(keys_list,items))
            corrected_line_item = json.loads(corrected_line_item)
            line_item['line_item_table'] = corrected_line_item
    return line_items

def return_invoice_lts(filtered_invoice_img_paths):
    financial_summary_template = {"subtotal":"",
	"hst":"",
	"total":"",}
    extracting_financial_summary_prompt = f'''### Read carefully through the invoice and extract the financial summary of the invoice.
    ### Validate your output against the following rules:
    # 1. The subtotal should be the sum of all the line items in the invoice.
    # 2. The HST should be the harmonized sales tax of the invoice.
    # 3. The total should be the sum of the subtotal and the HST.
    # 4. Return your output as JSON based on the following template: {financial_summary_template}'''
    normal_line_items = []
    financial_summaries = []
    for i in range(len(filtered_invoice_img_paths)):
        financial_summary = chat_with_4o(extracting_financial_summary_prompt,encode_image(filtered_invoice_img_paths[i]))
        financial_summary = json.loads(financial_summary)
        financial_summaries.append(financial_summary)
        formatted_line_items = validate_single_call(extract_line_items(encode_image(filtered_invoice_img_paths[i]))) 
        
        normal_line_items.append(formatted_line_items)
    return normal_line_items,financial_summaries

def final_ln_eval(filtered_ln_a,filtered_sk_a,filtered_metadata_ln_overlap):
    # filtered_sk_keys = get_dict_keys(filtered_sk_a)
    # filtered_sk_a = get_dict_values(filtered_sk_a)
    successful_ones,failed_ones,errors= [],[],[]
    for i in range(len(filtered_metadata_ln_overlap)):
        try:
            if validate_line_item_total(filtered_ln_a[i],filtered_sk_a[i]) == True:
                successful_ones.append(i)
            else:
                failed_ones.append(i)
            pass
        except Exception as e:
            errors.append((i,e))
    return successful_ones,failed_ones,errors

def try_catch_wrap_json(json_data):
    try:
        json.loads(json_data)
        return True
    except:
        return False
    
def wrapper_field_check(dict_,term='purchase_order_no'):
    return False if dict_[term] in ['','None','null',None] else True 

def wrapper_key_check(dict_,term = 'purchase_order_no'):
    return False if term not in list(dict_.keys()) else True 


def convert_tif_to_png(source_folder, destination_folder):
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Iterate over all files in the source folder
    for filename in os.listdir(source_folder):
        if filename.endswith(".tif"):
            # Open the .tif image
            try:
                img = Image.open(os.path.join(source_folder, filename))
                # Convert the image to .png format
                png_filename = os.path.splitext(filename)[0] + ".png"
                img.save(os.path.join(destination_folder, png_filename), "PNG")
                print(f"Converted {filename} to {png_filename}")
            except Exception as e:
                print(f"Error converting {filename}: {e}")
                continue


def clean_values(sample):
    for dict in sample['invoice_items']:
        validated_dict = json.loads(dict) if type(dict)==str else dict
        key_list = list(validated_dict.keys())
        for key in key_list:
            dict[key] = 0 if dict[key] == 'Not available' else dict[key]
    return sample


def check_invoice_output_wrapper(invoice_data):
    remove_parentheses = lambda str: str.replace('(','').replace(')','')
    remove_comma = lambda x:x.replace(',','')
    remove_currency_sign = lambda x:x.replace('$','')
    check_for_null = lambda x: 0 if x =='' else x
    check_for_str = lambda x: x if isinstance(x,str) else str(x)
    def try_catch_wrapper(element):
        try:
            return_value = round(float(check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(element)))))),2)
            return return_value
        except:
            var = check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(element)))))
            final_variable = ast.literal_eval(re.sub(r'[^\d.]', '', var))
            return final_variable if final_variable!='' else 0 
    derived_total = 0
    for dict_ in invoice_data['invoice_items']:
        
        dict_['item_total'] = try_catch_wrapper(dict_['item_total'])
        derived_total += dict_['item_total']

    actual_total = round(float(check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(invoice_data['invoice_total'])))))),2) 
    actual_tax = round(float(check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(invoice_data['invoice_tx'])))))),2)
    if round(derived_total + actual_tax,2) == actual_total:
        return True
    else:
        return False


def visualize_date_spread(column_name:str,df,bin_size=30):
    df[column_name] = pd.to_datetime(df[column_name]) if type(df[column_name].iloc[0]) != PANDAS_DATETYPE else df[column_name]
    binSize = timedelta(days=bin_size)
    bin_edges = pd.date_range(start=df[column_name].min(), end=df[column_name].max(), freq=binSize)
    plt.figure(figsize=(12, 6))
    plt.hist(df[column_name], bins=bin_edges, edgecolor='blue')

    # Customize the plot
    plt.title('Histogram of Dates')
    plt.xlabel('Date')
    plt.ylabel('Frequency')


def find_duplicate_indices(lst):
    from collections import defaultdict

    # Dictionary to store the indices of each element
    indices_dict = defaultdict(list)

    # Iterate through the list and store the indices
    for index, value in enumerate(lst):
        indices_dict[value].append(index)

    # Filter out the elements that have more than one index
    duplicates = {key: indices for key, indices in indices_dict.items() if len(indices) > 1}

    return duplicates

def removing_duplicate_invoices(duplicated_invoice_names):
    invoice_data = ast.literal_eval(read_txt_file(duplicated_invoice_names))
    extracted_names = get_last_elements(invoice_data)
    duplicate_entries = find_duplicate_indices(extracted_names)
    duplicate_keys = list(duplicate_entries.keys())
    cleaned_keys = [index for index,key in enumerate(extracted_names) if key not in duplicate_keys]
    cleaned_names = sublisting(extracted_names,cleaned_keys)
    cleaned_invoices = sublisting(get_first_elements(invoice_data),cleaned_keys)
    return cleaned_names,cleaned_invoices


def check_paths_valid(paths_list):
    for path in paths_list:
        if not os.path.exists(path):
            print('wack')


def inspect_invoices(index,invoice_images_paths,invoices_metadata,):
    
    target_path = invoice_images_paths[index]
    target_metadata = invoices_metadata[index]
    print(target_metadata)
    Image.open(target_path).show()

def generate_invoice_metadata(invoice_paths,invoice_names,file_name):
    import ast
    failed_invoices = []
    if len(invoice_paths) != len(invoice_names):
        raise ValueError('Length of invoice paths and invoice names do not match')
    for index,invoice_path in enumerate(invoice_paths):
        invoice_extracts = ast.literal_eval(read_txt_file(file_name))
        try:
            invoice_extract = extract_text_from_image(invoice_path)
            invoice_extracts.append((invoice_extract,invoice_names[index]))
            write_txt_file(file_name,str(invoice_extracts))
            print(f'Extracted invoice {invoice_names[index]}')
        except:
            print('failed somehow')
            failed_invoices.append(invoice_names[index])
    final_invoice_extracts = ast.literal_eval(read_txt_file(file_name))
    return final_invoice_extracts,failed_invoices

def remove_multi_page_invoices(all_invoice_names,extension='1_1.png'):
    multi_page_rejected = [element for element in all_invoice_names if element[-5:-4] != '1']
    source_multi_page_rejected = [re.sub(element[-7:],extension,element) for element in all_invoice_names if element in multi_page_rejected]
    all_multis = source_multi_page_rejected + multi_page_rejected
    cleaned_list_indices = [index for index,invoice in enumerate(all_invoice_names) if invoice not in all_multis]
    cleaned_list = sublisting(all_invoice_names,cleaned_list_indices)

    return cleaned_list,cleaned_list_indices

def wrapper_validate_tax_total(invoice_dict):
    remove_parentheses = lambda str: str.replace('(','').replace(')','')
    remove_comma = lambda x:x.replace(',','')
    remove_currency_sign = lambda x:x.replace('$','')
    check_for_null = lambda x: 0 if x =='' else x
    check_for_str = lambda x: x if isinstance(x,str) else str(x)
    try:
        round(float(check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(invoice_dict['invoice_total'])))))),2) and \
        round(float(check_for_null(remove_comma(remove_currency_sign(remove_parentheses(check_for_str(invoice_dict['invoice_tx'])))))),2)
        return True
    except:
        return False