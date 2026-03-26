import threading
import webview
from app import app

def run_flask():
    app.run(debug=False, use_reloader=False)

threading.Thread(target=run_flask, daemon=True).start()
webview.create_window("Mon application", "http://127.0.0.1:5000")
webview.start()