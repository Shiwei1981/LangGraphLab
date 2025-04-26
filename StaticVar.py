import tiktoken
import os
import json

api_key = os.getenv("AZURE_OPENAI_API_KEY")  
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
model_name = os.getenv("AZURE_OPENAI_MODEL_NAME") 
model_name_emb = os.getenv("AZURE_OPENAI_MODEL_NAME_EMB") 
model_name_reasoning = os.getenv("AZURE_OPENAI_MODEL_NAME_REASONING") 
model_name_reasoning_mini = os.getenv("AZURE_OPENAI_MODEL_NAME_REASONING_MINI") 

total_token = dict()

def cal_toten(model_name:str, prompt_str:str, output:str):
    global total_token
    total_in = 0
    total_out = 0
    for entry in total_token:  
        if entry == model_name:  
            total_in = total_token[entry]["total_token_in"]  
            total_out = total_token[entry]["total_token_out"]  
            break  
    encoding = tiktoken.get_encoding("cl100k_base")  
    total_in = total_in + len(encoding.encode(prompt_str))
    if output is not None:
        total_out = total_out + len(encoding.encode(output))
    total_token[model_name] = {"total_token_in": total_in, "total_token_out": total_out}

def print_toten()->str:
    global total_token
    return_str = json.dumps(total_token, indent=4, ensure_ascii=False)
    print(return_str)
    return return_str


def get_para(paraname: str) -> str:  
    try:  
        # 尝试打开 config.json 文件  
        with open('config.json', encoding='utf-8') as config_file:  
            config_data = json.load(config_file)  
    except FileNotFoundError:  
        raise Exception("Config file 'config.json' not found.")  
    except json.JSONDecodeError:  
        raise Exception("Error decoding JSON from 'config.json'.")  
    except Exception as e:  
        raise Exception(f"An unexpected error occurred: {e}")  
    # 检查参数是否存在于配置数据中  
    if paraname not in config_data:  
        raise Exception("Can't find value in config.json")  
    result = config_data[paraname]  
    # 如果值为 None 或者空字符串，也抛出异常  
    if result is None or result == "":  
        raise Exception("Value in config.json is empty or None")  
    
    return result  
