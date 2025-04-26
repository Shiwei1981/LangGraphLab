from http.server import SimpleHTTPRequestHandler, HTTPServer  
import urllib.parse  
from HRAgent import HRAgent
import json
from CommonFunc import quick_query
from StaticVar import print_toten
from StaticVar import get_para


# 定义请求处理类，继承自 SimpleHTTPRequestHandler  
class MyHandler(SimpleHTTPRequestHandler):  
    def do_POST(self):  
        content_length = int(self.headers['Content-Length'])  
        post_data = self.rfile.read(content_length).decode('utf-8')  
        parsed_data = urllib.parse.parse_qs(post_data)  
          
        # 路径为 /methodA 时调用方法 A  
        if self.path == "/answerquestion":  
            if "question" in parsed_data:  
                question = parsed_data["question"][0]  
                decoded_str = urllib.parse.unquote(question)
                result = answerquestion(decoded_str)  
                self.respond(result)  
            else:  
                self.send_error(400, "Bad Request: missing 'question' parameter")  
  
        # 路径为 /methodB 时调用方法 B  
        elif self.path == "/quickquery":  
            if "question" in parsed_data:   
                question = parsed_data["question"][0]  
                decoded_str = urllib.parse.unquote(question)
                result = quickquery(decoded_str)  
                self.respond(result)   
            else:  
                self.send_error(400, "Bad Request: missing 'question' parameter")   
        
        elif self.path == "/gettoken":  
                result = print_toten()  
                self.respond(result)   

        else:  
            self.send_error(404, "Not Found")  
  
    def respond(self, message):  
        self.send_response(200)  
        self.send_header("Content-type", 'application/json; charset=utf-8')  
        self.end_headers()  
        self.wfile.write(message.encode())  
  
def answerquestion(question:str):  
    hr_Agent = HRAgent()
    context = hr_Agent.load_context()
    hr_Agent.add_context(context)
    activitylist = hr_Agent.analyze_question(hr_Agent.contexts[0].sessionID, question)
    print('\n\nquestion answered!')
    context.activity_list = activitylist
    hr_Agent.update_context(context)

    json_str = json.dumps(activitylist, ensure_ascii=False, indent=4)
    return json_str  
  
def quickquery(question:str):  
    return quick_query(question) 
  
def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):  
    server_address = ('', port)  
    httpd = server_class(server_address, handler_class)  
    print(f"Serving on port {port}...")  
    httpd.serve_forever()  
  
def main():  
    run()  
  
if __name__ == "__main__":  
    main()  