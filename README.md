# AI Agent with Lang Graph Lab Codes  
  
Here I'll provide my lab codes for building an AI Agent with Lang Graph. The code will be written in Python.  

# HRAgentHTTPSVR.py and HRAgent.py Overview  
  
## HRAgentHTTPSVR.py  
**English:** HRAgentHTTPSVR.py establishes an HTTP service and serves as the entry point of the program.    
**中文:** HRAgentHTTPSVR.py 建立了一个 HTTP 服务，是程序入口。  
  
## HRAgent.py  
**English:** HRAgent.py is an agent example for HR. The `analyze_question` method is the main function of the demo. It first deconstructs the customer's question into a structured JSON. The JSON itself maintains one root, and all other nodes are children of the root. The JSON includes a "node number" field to indicate the specific location of the deconstruction task.    
**中文:** HRAgent.py 是一个以 HR 为例子的 Agent。`analyze_question` 方法是 demo 的主要程序。`analyze_question` 首先拆解客户的问题，拆解成一个有结构的 JSON，JSON 本身保持 1 个 root，其他所有节点都是 root 的子节点的构造，但是 JSON 内部有一个“节点编号”的字段，用于标志拆解任务的具体位置。  
  
## CommonFunc.py  
**English:** CommonFunc.py encapsulates the specific execution code. The construction of the langgraph is completed through the `generate_graph` function. This function retrieves the deconstructed JSON from the upper layer and constructs the Langgraph based on the "node number" in the JSON content. To enable the Langgraph to process tasks, three functions are defined: `is_there_todo_summary` - used for the condition judgement edge; `node_task` - handles tasks (currently pseudocode); `node_summary` - handles summaries (currently pseudocode).    
**中文:** CommonFunc.py 封装了具体的执行代码。langgraph 的构造通过 `generate_graph` 函数完成。`generate_graph` 函数获取上层拆解的 JSON，并根据 JSON 内容的“节点编号”，来构造 Langgraph。为了让 Langgraph 完成任务处理，定义了三个函数：`is_there_todo_summary` - 用于 condition 的判断 edge；`node_task` 用于处理 task（task 处理目前是伪码）；`node_summary` 用于处理 summary（summary 处理目前是伪码）。  
  
## Future Developments  
**English:** A frontend program will be added in the future.    
**中文:** 未来会增加一个前端程序。  
  
## Additional Information  
**English:** Currently, only simple comments are written. The program itself can run. If there are any issues, please contact me directly. Thank you.    
**中文:** 现在只是简单的写了些注释。程序本身是可以运行的。如果有问题，直接联系我本人。多谢。  
