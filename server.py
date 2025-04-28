import socket
import threading
import os
import datetime
import mimetypes
import time
import base64
import logging

class WebServer:
    def __init__(self, host='127.0.0.1', port=8080, root_dir='./www'):
        self.host = host
        self.port = port
        self.root_dir = root_dir
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.log_file = 'server_log.txt'
        
        # 确保网站根目录存在
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
            
        # 配置日志
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('WebServer')
        
    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.logger.info(f"服务器启动在 http://{self.host}:{self.port}")
        print(f"服务器启动在 http://{self.host}:{self.port}")
        
        try:
            while True:
                client_socket, client_address = self.socket.accept()
                self.logger.info(f"接受来自 {client_address} 的连接")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            self.logger.info("服务器关闭")
            print("服务器关闭")
        finally:
            self.socket.close()
            
    def handle_client(self, client_socket, client_address):
        keep_alive = True
        
        while keep_alive:
            try:
                request_data = b''
                while True:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    request_data += chunk
                    if b'\r\n\r\n' in request_data:
                        break
                
                if not request_data:
                    break
                
                # 尝试解码请求数据
                try:
                    request_str = request_data.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果无法解码，可能是二进制数据
                    self.logger.error("无法解码请求数据")
                    response = self.create_response('400', 'Bad Request', '', client_address)
                    client_socket.sendall(response.encode('utf-8'))
                    break
                
                # 第一阶段：显示请求内容
                self.logger.info(f"从 {client_address} 收到请求:\n{request_str}")
                
                # 第二阶段：解析请求并生成响应
                response, keep_alive = self.generate_response(request_str, client_address)
                
                # 发送响应
                if isinstance(response, str):
                    client_socket.sendall(response.encode('utf-8'))
                else:
                    client_socket.sendall(response)
                
                if not keep_alive:
                    break
                    
            except Exception as e:
                self.logger.error(f"处理客户端请求时出错: {e}")
                break
                
        client_socket.close()
        
    def generate_response(self, request_data, client_address):
        # 解析请求
        request_lines = request_data.split('\r\n')
        request_line = request_lines[0].split()
        
        if len(request_line) < 3:
            return self.create_response('400', 'Bad Request', '', client_address), False
        
        method = request_line[0]
        path = request_line[1]
        protocol = request_line[2]
        
        # 记录请求方法和路径
        self.logger.info(f"请求方法: {method}, 路径: {path}")
        
        # 默认为非持久连接
        keep_alive = False
        
        # 解析头部字段
        headers = {}
        for line in request_lines[1:]:
            if not line:
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        # 检查Connection头部字段
        if 'connection' in headers:
            if headers['connection'].lower() == 'keep-alive':
                keep_alive = True
                self.logger.info("持久连接: 是")
            else:
                self.logger.info("持久连接: 否")
        
        # 处理根路径
        if path == '/':
            path = '/index.html'
        
        # 构建文件路径
        file_path = os.path.join(self.root_dir, path.lstrip('/'))
        self.logger.info(f"访问文件: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.logger.warning(f"文件不存在: {file_path}")
            return self.create_response('404', 'Not Found', '', client_address, request_path=path), keep_alive
        
        # 检查文件是否可读
        if not os.access(file_path, os.R_OK):
            self.logger.warning(f"文件无法访问: {file_path}")
            return self.create_response('403', 'Forbidden', '', client_address, request_path=path), keep_alive
        
        # 获取文件的MIME类型
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        self.logger.info(f"内容类型: {content_type}")
        
        # 检查MIME类型是否支持
        supported_types = ['text/html', 'text/plain', 'text/css', 'application/javascript', 
                         'image/jpeg', 'image/png', 'image/gif']
        if content_type not in supported_types:
            self.logger.warning(f"不支持的媒体类型: {content_type}")
            return self.create_response('415', 'Unsupported Media Type', '', client_address, request_path=path), keep_alive
        
        # 获取文件最后修改时间
        last_modified = os.path.getmtime(file_path)
        last_modified_str = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(last_modified))
        
        # 检查If-Modified-Since
        if 'if-modified-since' in headers:
            try:
                if_modified_since = time.strptime(headers['if-modified-since'], '%a, %d %b %Y %H:%M:%S GMT')
                if_modified_since = time.mktime(if_modified_since)
                if last_modified <= if_modified_since:
                    self.logger.info("文件未修改")
                    return self.create_response('304', 'Not Modified', '', client_address, 
                                              last_modified_str, request_path=path), keep_alive
            except ValueError:
                self.logger.warning(f"无效的If-Modified-Since: {headers['if-modified-since']}")
        
        # 根据请求方法处理
        if method == 'HEAD':
            # HEAD方法只返回头部，不返回内容
            self.logger.info("HEAD请求 - 只返回头部")
            return self.create_response('200', 'OK', '', client_address, 
                                       last_modified_str, content_type, request_path=path), keep_alive
        
        elif method == 'GET':
            # GET方法返回头部和内容
            self.logger.info("GET请求 - 返回头部和内容")
            file_size = os.path.getsize(file_path)
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                if content_type.startswith('text'):
                    content = f.read().decode('utf-8')
                    return self.create_response('200', 'OK', content, client_address, 
                                              last_modified_str, content_type, request_path=path), keep_alive
                else:
                    # 对于二进制文件(图片等)，直接返回二进制数据
                    headers = self.create_headers('200', 'OK', file_size, last_modified_str, content_type, keep_alive)
                    response = headers.encode('utf-8') + b'\r\n\r\n' + f.read()
                    
                    # 记录日志
                    self.log_request(client_address[0], path, '200', 'OK')
                    
                    return response, keep_alive
        else:
            # 不支持的方法
            self.logger.warning(f"不支持的方法: {method}")
            return self.create_response('400', 'Bad Request', '', client_address, request_path=path), keep_alive
    
    def create_headers(self, status_code, status_text, content_length, last_modified=None, content_type=None, keep_alive=False):
        current_time = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        headers = [
            f"HTTP/1.1 {status_code} {status_text}",
            f"Date: {current_time}",
            "Server: PythonWebServer/1.0"
        ]
        
        if content_type:
            headers.append(f"Content-Type: {content_type}")
        
        if last_modified:
            headers.append(f"Last-Modified: {last_modified}")
        
        headers.append(f"Content-Length: {content_length}")
        
        if keep_alive:
            headers.append("Connection: keep-alive")
        else:
            headers.append("Connection: close")
            
        return '\r\n'.join(headers)
            
    def create_response(self, status_code, status_text, content, client_address, 
                      last_modified=None, content_type=None, request_path='/'):
        headers = self.create_headers(status_code, status_text, len(content), 
                                    last_modified, content_type)
        
        response = headers + '\r\n\r\n' + content
        
        # 记录日志
        self.log_request(client_address[0], request_path, status_code, status_text)
        
        return response
    
    def log_request(self, client_ip, request_path, status_code, status_text):
        with open(self.log_file, 'a') as f:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{client_ip} - {current_time} - {request_path} - {status_code} {status_text}\n"
            f.write(log_entry)
            

def create_sample_files(www_dir):
    """创建示例文件用于测试"""
    # 创建HTML文件
    with open(os.path.join(www_dir, 'index.html'), 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Web服务器演示</title>
            <link rel="stylesheet" href="styles.css">
            <script src="script.js"></script>
        </head>
        <body>
            <h1>Web服务器工作中!</h1>
            <p>这是一个简单的Web服务器演示页面。</p>
            <img src="image.jpg" alt="示例图片" />
            <button onclick="showMessage()">点击我</button>
        </body>
        </html>
        """)
    
    # 创建CSS文件
    with open(os.path.join(www_dir, 'styles.css'), 'w') as f:
        f.write("""
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        h1 {
            color: navy;
        }
        """)
    
    # 创建JavaScript文件
    with open(os.path.join(www_dir, 'script.js'), 'w') as f:
        f.write("""
        function showMessage() {
            alert('你好，这是一个测试消息！');
        }
        """)
    
    print("示例文件已创建")


if __name__ == '__main__':
    www_dir = './www'
    
    # 创建www目录用于存放网页文件
    if not os.path.exists(www_dir):
        os.makedirs(www_dir)
        
    # 创建示例文件
    create_sample_files(www_dir)
    
    # 启动服务器
    server = WebServer(host='127.0.0.1', port=8080, root_dir=www_dir)
    server.start() 