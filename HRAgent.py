import json
from typing import List 
import uuid
from CommonFunc import get_para, LLM_Prompt_question_analyze
from CommonFunc import generate_graph
from langgraph.graph import START, END
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from StaticVar import get_para

# 定义HRAgentContext类  
class HRAgentContext:
    def __init__(self, sessionID):  
        self.sessionID = sessionID  # 定义属性 name  
        self.messages_history = [] # 消息历史记录
        self.customerprofile = ""
        self.activity_list = {} # JSON 对象
        self.activity_content = {} # JSON 对象 包含每一个 activity 的输出结果
        self.customer_CSV_files = {} # CSV文件路径列表：{"file_path": "/path/to/file2.txt","file_description": "This is the second file."}
        self.customer_PDF_files = {} # PDF文件路径列表：{"file_path": "/path/to/file2.txt","file_description": "This is the second file."}
        self.question_analyze_prompt_template = "" # 问题分析提示模板
        self.question_analyze_result_content = "" # 问题必要的内容
        self.question_analyze_result_requirement = ""
        self.question_analyze_system_prompt = ""
        self.question = ""

# 定义HRAgent类  
class HRAgent:  
    # 初始化方法，__init__ 是一个特殊方法，用于初始化对象  
    def __init__(self, contexts:List[HRAgentContext]):  
        self.contexts = contexts
  
    def __init__(self):  
        self.contexts = []

    def load_context(self) -> HRAgentContext:
        guid = uuid.uuid4()
        guid_str = str(guid)
        context = HRAgentContext(guid_str)
        context.customerprofile = get_para("customerprofile")
        context.customer_CSV_files = get_para("customer_CSV_files")
        context.customer_PDF_files = get_para("customer_PDF_files")
        context.question_analyze_prompt_template = " ".join(get_para("question_analyze_prompt_template"))
        context.question_analyze_result_content = " ".join(get_para("question_analyze_result_content"))
        context.question_analyze_result_requirement = " ".join(get_para("question_analyze_result_requirement"))
        context.question_analyze_system_prompt = get_para("question_analyze_system_prompt")
        return context

    def save_context_activity_content(self, sessionID:str):
        context = self.find_context_with_SessionID(sessionID)
        json_file_path = 'save_context_activity_content.json'  
        with open(json_file_path, 'w', encoding='utf-8') as file:  
            json.dump(context.activity_content, file, ensure_ascii=False, indent=4)  

    def add_context(self, context:HRAgentContext):
        self.contexts.append(context)

    def remove_context(self, sessionID:str):
        self.contexts.remove(self.find_context_with_SessionID(sessionID))

    def update_context(self, context:HRAgentContext):
        self.remove_context(context.sessionID)
        self.add_context(context)

    # 定义一个方法  
    def find_context_with_SessionID(self, sessionID:str) -> HRAgentContext:
        for obj in self.contexts:  
            if (obj.sessionID == sessionID):
                return obj
        return None

    def analyze_question(self, sessionID:str, question:str) -> dict:
        Context = self.find_context_with_SessionID(sessionID)
        self.question = question
        
        csv_file_paths = [file['file_path'] for file in Context.customer_CSV_files]  
        csv_file_paths_str = ', '.join(f"'{file}'" for file in csv_file_paths)
        pdf_file_paths = [file['file_path'] for file in Context.customer_PDF_files]  
        pdf_file_paths_str = ', '.join(f"'{file}'" for file in pdf_file_paths)

        #字符串拼接两次
        question_analyze_prompt_message = Context.question_analyze_prompt_template.format(
            customerprofile=Context.customerprofile,
            question=question,
            question_analyze_result_content=Context.question_analyze_result_content,
            question_analyze_result_requirement=Context.question_analyze_result_requirement
        )


        question_analyze_prompt_message = question_analyze_prompt_message.format(
            area_number=get_para("area_number"),
            task_number=get_para("task_number"),
            customer_CSV_files=csv_file_paths_str,
            customer_PDF_files=pdf_file_paths_str
            # o1 模型 每个任务 1W5 个 in_token, 2k5 个 out
        )
        """
        # 临时代码 load prompt
        file_name = "example.txt"  
        # 读取 .txt 文件的内容  
        with open("example.txt", 'r', encoding='utf-8') as file:  
            question_analyze_prompt_message = file.read()  
        """
            
        question_analyze_prompt = [SystemMessage(Context.question_analyze_system_prompt), HumanMessage(question_analyze_prompt_message)]

        ##临时注释掉，为了测试 langgraph
        print("\n\n"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\nPrompt: \n", question_analyze_prompt_message)
        response = LLM_Prompt_question_analyze(question_analyze_prompt)
        print("\n\n"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\nResponse: \n", response)

        ## log
        msg_json = []
        for msg in question_analyze_prompt:  
            msg_json.append({  
                "role": msg.type,      # system／human  
                "content": msg.content # 消息文本  
            })  
        #question_analyze_prompt_json = [{"role": role, "message": message} for role, message in question_analyze_prompt]   
        with open('question_analyze_prompt.json', 'w', encoding='utf-8') as f:  
            json.dump(msg_json, f, ensure_ascii=False,indent=4)  
        question_analyze_reponse_json = json.loads(response)
        with open('question_analyze_response.json', 'w', encoding='utf-8') as f:  
            json.dump(question_analyze_reponse_json, f, ensure_ascii=False,indent=4)  
        
        ## 构造 测试数据
        with open('question_analyze_response.json', 'r', encoding='utf-8') as file: 
            question_analyze_response_json = json.load(file)  

        ## 基于 question_analyze_prompt_json 内容 构造 LangGraph
        question_analyze_result = generate_graph(question_analyze_response_json, self.question)

        with open('question_analyze_result.json', 'w', encoding='utf-8') as f:  
            json.dump(question_analyze_result["tasks_json"]['root'], f, ensure_ascii=False,indent=4) 

        return question_analyze_result