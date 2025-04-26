import logging
import json
from typing import List
from langchain_openai import AzureChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated,List
from IPython.display import Image, display
from langgraph.graph.message import add_messages
import time
from MCPClientManager import mcp_init_and_process_query
import asyncio
from StaticVar import api_key, endpoint, api_version, model_name, model_name_emb, model_name_reasoning, model_name_reasoning_mini
from StaticVar import cal_toten
from StaticVar import get_para

# 创建日志器  
logger = logging.getLogger('my_logger')  
logger.setLevel(logging.DEBUG)  # 设置日志器的日志级别  
  
# 创建文件处理器，并设置编码为 utf-8  
file_handler = logging.FileHandler('app.log', encoding='utf-8')  
file_handler.setLevel(logging.DEBUG)  # 设置文件处理器的日志级别  
  
# 创建格式化器  
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
file_handler.setFormatter(formatter)  # 将格式化器应用到文件处理器  
  
# 将文件处理器添加到日志器  
logger.addHandler(file_handler)  


# langgraph 状态总是不对，怀疑是并发问题，加一个状态锁
state_json_task_status_lock = "release"

env={
        "AZURE_OPENAI_API_KEY":api_key,
        "AZURE_OPENAI_ENDPOINT":endpoint,
        "AZURE_OPENAI_API_VERSION":api_version,
        "AZURE_OPENAI_MODEL_NAME":model_name,
        "AZURE_OPENAI_MODEL_NAME_EMB":model_name_emb        
    } 

def LLM_Prompt_question_analyze(messages: List[str]) -> str:
    model = AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        model=model_name_reasoning
    )
    response = model.invoke(messages)
    contents = [message.content for message in messages]  
    prompt_str = "".join(contents)  
    cal_toten(model_name = model_name_reasoning, prompt_str=prompt_str, output = response.content)
    return response.content

def LLM_Prompt_task_execute(messages: List[str]) -> str:
    model = AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        model=model_name,
        temperature=0
    )    
    response = model.invoke(messages)
    contents = [message.content for message in messages]  
    prompt_str = "".join(contents)  
    cal_toten(model_name = model_name_reasoning, prompt_str=prompt_str, output = response.content)
    return response.content

def LLM_Prompt_outcome_summarize(messages: List[str]) -> str:
    model = AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        model=model_name,
        temperature=0
    )    
    response = model.invoke(messages)
    contents = [message.content for message in messages]  
    prompt_str = "".join(contents)  
    cal_toten(model_name = model_name_reasoning, prompt_str=prompt_str, output = response.content)
    return response.content

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    messages_history: Annotated[list[AnyMessage], add_messages]
    tasks_json: dict
    questioin: str

def node_task(state: AgentState):
    ##首先决定做哪一个task，寻找第一个状态是 "待分析" 的 task
    global state_json_task_status_lock
    while True:
        # 查一下锁
        if state_json_task_status_lock == "release":
            state_json_task_status_lock = "lock"
            task_str = ""
            last_assistant_str = ""
            task_json = find_first_todo_task(state["tasks_json"])
            
            #trace
            logger.info("进入节点执行，当前节点是 {nodeid} \n".format(nodeid=task_json["Metadata-节点编号"]))
            
            if task_json is None:
                raise ValueError("出现了异常，节点开始执行，但是，JSON 中并没有找到 “待分析”的节点")
            try:
                if task_json["Metadata-节点类型"] == "分析方法":
                    task_json["Metadata-状态"] = "开始执行"  
                    #task_str = json.dumps(task_json, ensure_ascii=False)
                    task_str = generate_task_prompt_from_JSON(task_json, task_json["Metadata-节点类型"], question=state["questioin"])
                    messages =  asyncio.run(mcp_init_and_process_query(task_str))
                    for message in messages:  
                        if message["role"] == "assistant":  
                            last_assistant_str = message["content"]  
                elif (task_json["Metadata-节点类型"] == "分析领域") or (task_json["Metadata-节点类型"] == "总述"):
                    ##首先决定做哪一个task，寻找第一个状态是 "待分析" 的 task
                    task_json["Metadata-状态"] = "开始总结"  
                    previouse_outputs = ""
                    for node in state["tasks_json"]["root"]:
                        if node['Metadata-父节点编号'] == task_json["Metadata-节点编号"]:  
                            previouse_outputs = previouse_outputs + "\n\n --- \n" + node['输出']
                    summary_prompt_str = generate_summary_prompt_from_JSON(
                        question=state["questioin"],
                        previouse_messages_str=previouse_outputs
                    )
                    messages = [HumanMessage(summary_prompt_str)]
                    LLM = AzureChatOpenAI(
                        api_key=api_key,
                        api_version=api_version,
                        azure_endpoint=endpoint,
                        azure_deployment=model_name
                    )
                    response = LLM.invoke(messages)
                    last_assistant_str = response.content
                else:
                    task_str = "未正确获取task指令内容,指令类型是：" + task_json["Metadata-状态"]
                    last_assistant_str = " 状态错误-exception 了 "
            finally:
                task_json["输出"] = last_assistant_str
                task_json["Metadata-状态"] = "完成"  
                state["messages_history"].append(HumanMessage(task_str))
                state["messages_history"].append(AIMessage(last_assistant_str))
                state_json_task_status_lock = "release"

                # 为什么这里要 sleep? 测试了很长时间，发现如果 graph 采用深度优先遍历，则总是不执行节点1。
                # 只能增加一个 sleep，增加了之后，结合锁的sleep 时间，就手动调整了 广度优先 遍历，结果就好了。
                # 说实话，没搞懂为什么
                time.sleep(2)
                return
        else:
            time.sleep(0.5)

# 查找第一个 "状态": "待分析" 的节点及其上级节点  
def find_first_todo_task(data):  
    for child in data["root"]:  
        if child["Metadata-状态"] == "待分析":  
            return child  # 返回当前节点（根节点）
    return None  

## 寻找可以开始总结的领域。检查是否存在 子task 都完成的task，如果存在，状态为 待分析，并返回 "go"
def check_task_status(state: AgentState):  
    global state_json_task_status_lock
    result = "wait"
    while True:
        # 全都锁起来！
        if ((state_json_task_status_lock == "release")):
            state_json_task_status_lock = "lock"
            try:
                #trace
                completed_nodes = []
                for node in state["tasks_json"]['root']:  
                    if node["Metadata-状态"] == "完成":  
                        completed_nodes.append(node["Metadata-节点编号"]) 
                result_string = ', '.join(completed_nodes) 
                logger.info("进入节点寻找，此时JSON中完成的节点是： {node_numbers} \n".format(node_numbers=result_string))
                
                # 如果节点有子节点，递归遍历  
                # 创建一个字典来保存节点编号和对应节点信息  
                nodes = {item['Metadata-节点编号']: item for item in state["tasks_json"]['root']}  
                
                # 遍历每个节点  
                for item in state["tasks_json"]['root']:  
                    node_id = item['Metadata-节点编号']
                    
                    # 获取所有子节点  
                    children = [child for child in state["tasks_json"]['root'] if child['Metadata-父节点编号'] == node_id]  
                    # 检查所有子节点的状态  
                    if all(child['Metadata-状态'] == '完成' for child in children):  
                        logger.info("找到子节点全完成的节点。次节点是：{nodeid} 此节点的状态是 {status} \n".format(nodeid=node_id, status=nodes[node_id]['Metadata-状态']))
                        # 返回父节点信息                  
                        if nodes[node_id]['Metadata-状态'] == '等待':
                            nodes[node_id]['Metadata-状态'] = '待分析'
                            result = "go"
                            break
            finally:
                state_json_task_status_lock = "release"
                #trace
                if result == "wait":
                    logger.info("没有找到合适的节点，转向 END \n")
                return result
        else:
            time.sleep(2)

def generate_graph(question_analyze_response_json, question: str) -> dict:
    graph_builder = StateGraph(AgentState)

    for node in question_analyze_response_json["root"]:  
        node_id = node["Metadata-节点编号"]  
        node_type = node["Metadata-节点类型"]  
        parent_id = node["Metadata-父节点编号"]          
        node["输出"] = ""
        node["Metadata-状态"] = "等待"  
        graph_builder.add_node(node_id, node_task)

        #如果是节点1，则添加 与 END的关系
        if node_id == "1":
            graph_builder.add_edge(node_id, END)
            
        #判空
        node["Metadata-子节点编号"] = node["Metadata-子节点编号"].lower()
        node["Metadata-父节点编号"] = node["Metadata-父节点编号"].lower()
        if node["Metadata-子节点编号"] == "null":
            node["Metadata-子节点编号"] = ""
        if node["Metadata-父节点编号"] == "null":
            node["Metadata-父节点编号"] = ""

        #如果有父节点，则添加与父节点的关系
        if not node["Metadata-父节点编号"] == "":
            graph_builder.add_conditional_edges(node_id, check_task_status, {"go": parent_id, "wait": END})
            logger.info("添加了edge，{nodeid} - {pid} \n".format(nodeid=node_id, pid = parent_id))

        #没有子节点，则加一个 start-> node，再加一个 conditional 的 node->parent 或 end
        if node["Metadata-子节点编号"] == "":
            #添加与 Start 节点的关系
            graph_builder.add_edge(START, node_id)
            #没有子节点的节点，立刻启动，其他所有情况都 等待
            node["Metadata-状态"] = "待分析"
            

    graph = graph_builder.compile()

    ##display(Image(graph.get_graph().draw_mermaid_png()))
    initial_state = {"messages": [], "tasks_json": question_analyze_response_json, "questioin": question, "messages_history": []}

    print(graph.get_graph().draw_mermaid())

    #trace
    logger.info(graph.get_graph().draw_mermaid())

    graph.invoke(initial_state)

    return initial_state

def generate_task_prompt_from_JSON(node_json: dict, node_type: str, question:str) -> str:
    customer_profile=get_para("customerprofile")
    #return_str = ""
    task_json = dict()
    for key in node_json.keys():
        if not key.startswith("Metadata-"): 
            task_json[key] = node_json[key]
    task_str = json.dumps(task_json, ensure_ascii=False, indent=4)
    prompt_template_str = ''.join(get_para("taks_execution_prompt_template"))
    prompt_str = prompt_template_str.format(
        question=question, 
        customer_profile=customer_profile,
        task=task_str
        )
    return prompt_str

def generate_summary_prompt_from_JSON(question:str, previouse_messages_str:str) -> str:
    taks_summary_prompt_template = get_para("taks_summary_prompt_template")
    taks_summary_prompt_template_str = ''.join(taks_summary_prompt_template)
    customer_profile=get_para("customerprofile")    
    prompt_str = taks_summary_prompt_template_str.format(
        question=question, 
        customer_profile=customer_profile,
        task_results=previouse_messages_str
        )
    return prompt_str

def quick_query(question:str):      
    prompt_template_str = get_para("quick_query_prompt_template")
    messages =  asyncio.run(mcp_init_and_process_query(prompt_template_str.format(question=question)))
    last_assistant_str = ""
    for message in messages:  
        if message["role"] == "assistant":  
            last_assistant_str = message["content"]   
    return last_assistant_str
