import socket
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
import json5  # 需要安装 json5 库：pip install json5
import createSbsar

class PortListenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Port Listener")
        self.root.geometry("400x300")

        # 监听状态
        self.listening = False
        self.server_socket = None

        # UI 组件
        self.label = tk.Label(root, text="Port Listener", font=("Arial", 16))
        self.label.pack(pady=10)

        self.port_label = tk.Label(root, text="Enter Port:")
        self.port_label.pack()

        self.port_entry = tk.Entry(root)
        self.port_entry.insert(0, "24981")  # 设置默认值
        self.port_entry.pack()

        self.start_button = tk.Button(root, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Listening", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.log_label = tk.Label(root, text="Log:")
        self.log_label.pack()

        self.log_area = scrolledtext.ScrolledText(root, state='disabled', height=10)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def start_listening(self):
        port = self.port_entry.get()
        if not port.isdigit():
            messagebox.showerror("Error", "Please enter a valid port number.")
            return

        port = int(port)
        self.listening = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(5)

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.DISABLED)

        self.log("Started listening on port {}...".format(port))

        # 启动监听线程
        self.listen_thread = threading.Thread(target=self.listen_for_connections, daemon=True)
        self.listen_thread.start()

    def stop_listening(self):
        self.listening = False
        if self.server_socket:
            self.server_socket.close()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.NORMAL)
        self.log("Stopped listening.")

    def listen_for_connections(self):
        while self.listening:
            try:
                client_socket, client_address = self.server_socket.accept()
                # self.log("Connection from: {}".format(client_address))
                self.log(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+':begin cooker')

                # 接收完整数据
                data = self.receive_all_data(client_socket)
                if data:
                    # self.log("Received: {}".format(data))

                    # 解析 JSON5 数据
                    try:
                        data_dict = json5.loads(data)  # 将 JSON5 字符串解析为字典
                        # self.log("Parsed data: {}".format(data_dict))

                        # 调用 test(data) 函数
                        a = self.test(data_dict)
                        if a :
                            self.log('done')
                        else:
                            self.log(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ': cooker done')


                    except json5.JSONDecodeError as e:
                        self.log("Failed to parse JSON5: {}".format(e))

                client_socket.close()
            except OSError:
                break

    def receive_all_data(self, client_socket):
        buffer = b""
        while True:
            try:
                part = client_socket.recv(1024)  # 每次接收 1024 字节
                if not part:
                    break  # 如果没有数据，表示客户端关闭连接
                buffer += part
            except socket.timeout:
                break  # 超时退出
            except ConnectionResetError:
                break  # 客户端异常断开

        return buffer.decode('utf-8', errors='ignore')  # 解码为字符串

    def test(self, data):
        """
        测试函数，接收解析后的字典并处理。
        """
        a = createSbsar.run(data[0])
        return a

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state='disabled')
        self.log_area.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PortListenerApp(root)
    root.mainloop()