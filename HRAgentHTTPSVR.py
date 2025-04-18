from http.server import SimpleHTTPRequestHandler, HTTPServer  
import urllib.parse  
from HRAgent import HRAgent
import json
  
# 定义请求处理类，继承自 SimpleHTTPRequestHandler  
class MyHandler(SimpleHTTPRequestHandler):  
    def do_GET(self):  
        parsed_path = urllib.parse.urlparse(self.path)  
        query_params = urllib.parse.parse_qs(parsed_path.query)  
          
        # 路径为 /methodA 时调用方法 A  
        if parsed_path.path == "/answerquestion":  
            if "question" in query_params:  
                question = query_params["question"][0]  
                result = answerquestion(question)  
                self.respond(result)  
            else:  
                self.send_error(400, "Bad Request: missing 'str1' parameter")  
  
        # 路径为 /methodB 时调用方法 B  
        elif parsed_path.path == "/methodB":  
            if "str1" in query_params and "str2" in query_params:  
                str1 = query_params["str1"][0]  
                str2 = query_params["str2"][0]  
                result = method_B(str1, str2)  
                self.respond(result)  
            else:  
                self.send_error(400, "Bad Request: missing 'str1' or 'str2' parameter")  
          
        else:  
            self.send_error(404, "Not Found")  
  
    def respond(self, message):  
        self.send_response(200)  
        self.send_header("Content-type", "text/html")  
        self.end_headers()  
        self.wfile.write(message.encode())  
  
def answerquestion(question):  
    hr_Agent = HRAgent()
    context = hr_Agent.load_context()
    hr_Agent.add_context(context)
    activitylist = hr_Agent.analyze_question(hr_Agent.contexts[0].sessionID, question)
    context.activity_list = activitylist
    hr_Agent.update_context(context)

    json_str = json.dumps(activitylist, ensure_ascii=False, indent=4)
    return json_str  
  
def method_B(str1, str2):  
    return f"Received two strings: {str1} and {str2}"  
  
def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):  
    server_address = ('', port)  
    httpd = server_class(server_address, handler_class)  
    print(f"Serving on port {port}...")  
    httpd.serve_forever()  
  
def main():  
    run()  
  
if __name__ == "__main__":  
    main()  