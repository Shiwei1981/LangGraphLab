import json
import os
from typing import List
from langchain_openai import AzureChatOpenAI
import xml.etree.ElementTree as ET 
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
import operator
from typing import TypedDict, Annotated, Union, Optional,Type,List
from IPython.display import Image, display
from langgraph.graph.message import add_messages
import time


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

"""
messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        },
        {
            "role": "assistant",
            "content": "Paris, the capital of France, is known for its stunning architecture, art museums, historical landmarks, and romantic atmosphere. Here are some of the top attractions to see in Paris:\n \n 1. The Eiffel Tower: The iconic Eiffel Tower is one of the most recognizable landmarks in the world and offers breathtaking views of the city.\n 2. The Louvre Museum: The Louvre is one of the world's largest and most famous museums, housing an impressive collection of art and artifacts, including the Mona Lisa.\n 3. Notre-Dame Cathedral: This beautiful cathedral is one of the most famous landmarks in Paris and is known for its Gothic architecture and stunning stained glass windows.\n \n These are just a few of the many attractions that Paris has to offer. With so much to see and do, it's no wonder that Paris is one of the most popular tourist destinations in the world.",
        },
        {
            "role": "user",
            "content": "What is so great about #1?",
        }
    ],
"""
def LLM_Prompt_question_analyze(messages: List[str]) -> str:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")  
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    model_name = os.getenv("AZURE_OPENAI_MODEL_NAME") 
    model_name = "o3-mini" 
    model = AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        model=model_name,
        temperature=1
    )    
    response = model.invoke(messages)
    return response.content

def LLM_Prompt_task_execute(messages: List[str]) -> str:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")  
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    model_name = os.getenv("AZURE_OPENAI_MODEL_NAME") 
    model_name = "gpt-4" 
    model = AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        model=model_name,
        max_tokens=4096,
        temperature=0.7
    )    
    response = model.invoke(messages)
    return response.content

def LLM_Prompt_outcome_summarize(messages: List[str]) -> str:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")  
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    model_name = os.getenv("AZURE_OPENAI_MODEL_NAME") 
    model_name = "gpt-4" 
    model = AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        model=model_name,
        max_tokens=4096,
        temperature=0.7
    )    
    response = model.invoke(messages)
    return response.content

def langgraph_task_execute() -> str:
    return "langgraph_task_execute"

def langgraph_construct() -> str:
    return "langgraph_construct"

def xml_json(xml_data):
    # 解析 XML 数据
    root = ET.fromstring(xml_data)

    # 创建一个空的字典来存储 JSON 数据
    json_data = {}

    # 遍历 XML 元素并将其转换为字典
    for child in root:
        json_data[child.tag] = child.text

    return json_data

"""
def compare_sequence_numbers(seq_num1, seq_num2):  
    
    比较两个节点编号的大小  
  
    :param seq_num1: 第一个节点编号 (字符串)  
    :param seq_num2: 第二个节点编号 (字符串)  
    :return:   
        - 1: seq_num1 大于 seq_num2  
        - -1: seq_num1 小于 seq_num2  
        - 0: seq_num1 等于 seq_num2  
      
    # 将节点编号分割成整数元组  
    tuple1 = tuple(map(int, seq_num1.split('.')))  
    tuple2 = tuple(map(int, seq_num2.split('.')))  
  
    # 比较元组  
    if tuple1 > tuple2:  
        return 1  
    elif tuple1 < tuple2:  
        return -1  
    else:  
        return 0  
"""

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    tasks_json: dict

def node_task(state: AgentState):
    ##首先决定做哪一个task，寻找第一个状态是 "待分析" 的 task
    task_json = find_first_todo_task(state["tasks_json"])
    task_str = json.dumps(task_json, ensure_ascii=False)
    task_json["状态"] = "开始执行"  
    time.sleep(5)
    task_json["输出"] = "分析已完成，结果已记录" 
    task_json["状态"] = "完成"  
    return {"messages": HumanMessage(task_str)}

def node_summary(state: AgentState):
    ##首先决定做哪一个task，寻找第一个状态是 "待分析" 的 task
    task_json = find_first_todo_summary(state["tasks_json"])
    task_str = json.dumps(task_json, ensure_ascii=False)
    task_json["状态"] = "完成"  
    task_json["输出"] = "总结已完成，结果已记录" 
    return {"messages": HumanMessage(task_str)}

## 寻找可以开始总结的领域。检查是否存在 task 都完成的领域，如果存在，修改该领域的 状态为待开始，并返回 "go"
def is_there_todo_summary(data) -> str:  
    # 如果节点有子节点，递归遍历  
    result = "wait"
    # 创建一个字典来保存节点编号和对应节点信息  
    nodes = {item['节点编号']: item for item in data['root']}  
      
    # 遍历每个节点  
    for item in data['root']:  
        node_id = item['节点编号']
          
        # 获取所有子节点  
        children = [child for child in data['root'] if child['父节点编号'] == node_id]  
        # 检查所有子节点的状态  
        if all(child['状态'] == '完成' for child in children):  
            # 返回父节点信息                  
            if nodes[node_id]['状态'] == '等待':
                nodes[node_id]['状态'] = '待总结'
                result = "go"
                break
    return result

# 查找第一个 "状态": "待分析" 的节点及其上级节点  
def find_first_todo_task(data):  
    if data.get("状态") == "待分析":  
        return data  # 返回当前节点（根节点）  
      
    for child in data.get("root", []):  
        result = find_first_todo_task(child)  
        if result:  
            return result  # 返回找到的子节点  
    return None  

# 查找第一个 "状态": "待分析" 的节点及其上级节点  
def find_first_todo_summary(data):  
    if data.get("状态") == "待总结":  
        return data  # 返回当前节点（根节点）  
      
    for child in data.get("root", []):  
        result = find_first_todo_summary(child)  
        if result:  
            return result  # 返回找到的子节点  
    return None 

def check_summary_status(state: AgentState):
    """check if content ready"""
    result = is_there_todo_summary(state["tasks_json"])
    return result

def generate_graph(question_analyze_response_json) -> dict:
    graph_builder = StateGraph(AgentState)
    ##start_node = graph_builder.add_node(START, node_start, "start")
    ##end_node = graph_builder.add_node(END, node_summary, "end")
    

    for node in question_analyze_response_json["root"]:  
        node_id = node["节点编号"]  
        node_type = node["节点类型"]  
        parent_id = node["父节点编号"]  
        node["状态"] = "待分析"
        node["输出"] = ""

        if node_id == "1":
            graph_builder.add_node(node_id, node_summary) 
            graph_builder.add_edge(node_id, END)
            node["节点类型"] = "分析领域"
            node["状态"] = "等待"  
            continue

        if node_type == "分析领域":
            graph_builder.add_node(node_id, node_summary) 
            node["状态"] = "等待"
        
        if node_type == "分析方法":
            graph_builder.add_node(node_id, node_task)
            graph_builder.add_edge(START, node_id)
        
        graph_builder.add_conditional_edges(node_id, check_summary_status, {"go": parent_id, "wait": END})

    graph = graph_builder.compile()

    ##display(Image(graph.get_graph().draw_mermaid_png()))
    initial_state = {"messages": [], "tasks_json": question_analyze_response_json}

    print(graph.get_graph().draw_mermaid())

    graph.invoke(initial_state)

    return initial_state