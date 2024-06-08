import os
from posixpath import *
from urllib import parse
from cgi import parse_header, parse_multipart
from http.server import HTTPServer, BaseHTTPRequestHandler 
import io
import openai

apiKey = 'sk-EnpheLsfBvjZq7fG5aEteX6IbS0YA9dSmc89h2O53letSmSR'
#openai.api_key = apiKey
messages = [ {"role": "system", "content":  "You are a intelligent assistant."} ] 

client = openai.OpenAI(api_key=apiKey, base_url="https://api.chatanywhere.tech/v1")
msgs = []

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = parse.urlparse(self.path)
        query = parse.parse_qs(url.query)
        lastSeg = url.path.rsplit('/', 1)[-1]
        if lastSeg == "":
            lastSeg = "main.html"
        targetFilePath = os.path.join(os.getcwd(), 'hackPack2024', lastSeg)
        if not os.path.isfile(targetFilePath): 
            self.send_response(404, "It seems the page is missing!!!")
            self.end_headers()  
            return
        self.send_response(200)
        self.end_headers()  
        content = self.render(targetFilePath)
        content = content.replace("{{history}}", "")
        self.wfile.write(bytes(content,'utf-8'))
        # self.wfile.write('\n') 
        return
    
    def do_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        # if "boundary" in pdict:
        #     pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict, "utf-8")
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            wrapper = io.TextIOWrapper(self.rfile, encoding='utf-8')
            postData = wrapper.read(length)
            postvars = parse.parse_qs(postData, keep_blank_values=1)
        else:
            postvars = {}
        askMessage = postvars.get("askmessage")[0]
        messages.append( 
            {"role": "user", "content": askMessage}, 
        ) 
        print("before ask")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
            top_p=1,
            frequency_penalty=0,    
            presence_penalty=0)
        print(completion)
        reply = completion.choices[0].message.content 
        msgs.append(f"<span>{askMessage}</span> <br>")
        msgs.append(f"<span style='font-weight: bold;'>{reply}</span> <br>")
        # self.send_response(200)
        # self.end_headers() 
        # result = bytes(f'hello {content[0]}','utf-8')
        # self.wfile.write(result)
        url = parse.urlparse(self.path)
        lastSeg = url.path.rsplit('/', 1)[-1]
        if lastSeg == "":
            lastSeg = "main.html"
        targetFilePath = os.path.join(os.getcwd(), 'hackPack2024', lastSeg)
        if not os.path.isfile(targetFilePath): 
            self.send_response(404, "It seems the page is missing!!!")
            self.end_headers()  
            return
        self.send_response(200)
        self.end_headers()  
        content = self.render(targetFilePath)
        # finalmsg = "<ul> "
        # for x in msgs:
        #     finalmsg += f"<li>{x}</li>"
        # finalmsg += "</ul>"
        content = content.replace("{{history}}","".join(msgs))
        self.wfile.write(bytes(content,'utf-8'))
        return 

    def render(self, file_name='index'):
        html = open(file_name, 'r').read()
        return html            


if __name__ == '__main__':
    server = HTTPServer(('localhost', 2024), Handler)
    print('Development server is running at http://127.0.0.1:2024/')
    print('Starting server, use  to stop')
    server.serve_forever()