import webview

def start_webview():
    window = webview.create_window('Test Window', html='<h1>Hello World</h1>')
    webview.start()

if __name__ == '__main__':
    start_webview()
