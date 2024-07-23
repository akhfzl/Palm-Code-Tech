from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
from datetime import datetime
from dateutil import parser

def DialoGPT(name):
    # model pretrained
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name)

    return tokenizer, model

def GenerateResponse(text, is_time=False):
    if is_time:
        pass

    tokenizer, model = DialoGPT("microsoft/DialoGPT-medium")
    ids_input = tokenizer.encode(text + tokenizer.eos_token, return_tensors='pt')

    # give attention mask for reability model
    attention_mask = torch.ones(ids_input.shape, dtype=torch.long)

    # generate ids for chat
    chat_history_ids = model.generate(
        ids_input, 
        attention_mask=attention_mask,
        max_length=1000, 
        pad_token_id=tokenizer.eos_token_id
    )
    
    # decode ids with tokenizer
    return tokenizer.decode(chat_history_ids[:, ids_input.shape[-1]:][0], skip_special_tokens=True)

def time_format():
    return [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%b %d, %Y %H:%M:%S",
        "%d %b %Y %H:%M:%S",
        "%d-%b-%Y %H:%M:%S",
        "%d %B %Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%m/%d/%Y %H:%M",
        "%b %d, %Y %H:%M",
        "%d %b %Y %H:%M",
        "%d-%b-%Y %H:%M",
        "%d %B %Y %H:%M"
    ]

def patterns(teks):
    pattern = r"\b\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2}\b"
   
    result = re.fullmatch(pattern, teks)
    
    return result is not None

def time_extract(candidates):
    # if pattern isn't found in the text, the model pretrained will generates another answering
    if not candidates:
        return False 
    
    # return time format
    probability_format = time_format()

    result = []
    
    for candidate in candidates:
        try:
            # check parser candidate, approach 1
            time_object = parser.parse(candidate)
            result.append(time_object)
        except ValueError:
            # if not found the format by parse, it will use approach 2
            for format in probability_format:
                try:
                    time_object = datetime.strptime(candidate, format)
                    result.append(time_object)
                    break
                except ValueError:
                    continue
    
    return result if len(result) > 0 else False

def selection_time(pattern_extract):
    time_array = []
    result = []
    for extract in pattern_extract:
        time_result = date_selection(extract)

        if time_result:
            time_array.append(extract)
            result.append(time_result)

    return [set(time_array), set(result)] if len(time_array) > 0 and len(result) > 0 else False


def date_selection(text):
    # pattern regex for '-'
    pattern = r'\b\w+-\b\w+-\w+\b'
  
    result = re.search(pattern, text)
    
    if result:
        return result.group()
    else:
        pattern = r'\b\w+/\b\w+/\w+\b'
  
        result = re.search(pattern, text)
        
        if result:
            return result.group()
        else:
            pattern = r'\b\w+\s\b\w+\s\w+\b'
  
            result = re.search(pattern, text)

            if result:
                return result.group()
            else:
                return False
            
def time_selection(text):
    # pattern regex for '-'
    pattern = r'\b\w+:\b\w+:\w+\b'
  
    result = re.search(pattern, text)
    
    if result:
        return result.group()
    else:
        pattern = r'\b\w+:\w+\b'
  
        result = re.search(pattern, text)

        if result:
            return result.group()
        else:
            return False
            
def information_extract(teks):
    pattern = r'name:\s*"([^"]+)",\s*start_booked:\s*"([^"]+)",\s*end_booked:\s*"([^"]+)"'
 
    match = re.search(pattern, teks, re.DOTALL)
    
    if match:
        name = match.group(1)
        start_booked = match.group(2)
        end_booked = match.group(3)
        return {"name": name, "start": start_booked, "end": end_booked}
    else:
        return False
    

def check_range_zone(input_pattern, df):
    formatter = "%Y-%m-%d %H:%M:%S"
    start_formatted = datetime.strptime(input_pattern['start'], formatter)
    start_string = str(start_formatted.date())

    df_filter = df[df['Date'] == start_string]
    cond = True 

    for i in range(len(df_filter)):
        start = datetime.strptime(df_filter['time_start'][i], formatter)
        end = datetime.strptime(df_filter['time_end'][i], formatter)

        if start <= start_formatted <= end:
            cond = False

    return cond