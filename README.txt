# 多线程Web服务器

## 项目说明
这是一个使用Python实现的多线程Web服务器，支持HTTP协议的GET和HEAD请求，能够处理文本和图像文件，并实现了多种HTTP状态码响应。

## 功能特点
- 支持多线程并发处理请求
- 支持GET和HEAD命令
- 支持文本文件和图像文件
- 实现六种HTTP响应状态：200 OK、304 Not Modified、400 Bad Request、403 Forbidden、404 File Not Found、415 Unsupported Media Type
- 处理Last-Modified和If-Modified-Since头部字段
- 支持HTTP持久连接(keep-alive)和非持久连接(close)
- 记录请求日志

## 运行环境要求
- Python 3.6或更高版本
- 无需额外的第三方库

## 如何运行
1. 确保您的系统已安装Python 3.6+
2. 进入程序所在目录
3. 运行以下命令启动服务器：
   ```
   python server.py
   ```
4. 服务器默认运行在127.0.0.1:8080

## 访问服务器
服务器启动后，可以通过浏览器访问：
- http://127.0.0.1:8080

## 测试HEAD请求
可以使用curl命令测试HEAD请求：
```
curl -I http://127.0.0.1:8080
```

## 测试持久连接
可以使用curl命令测试持久连接：
```
curl -v -H "Connection: keep-alive" http://127.0.0.1:8080
```

## 日志文件
服务器会自动生成日志文件server_log.txt，记录每次请求的详细信息。 