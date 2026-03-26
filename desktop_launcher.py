import webview
import threading
import time
from app import app, db

def run_flask():
    app.run(port=5000)

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Wait a bit for the server to start
    time.sleep(2)

    # Create a pywebview window
    webview.create_window(
        'CliniAque - Gestion Nutritionnelle', 
        'http://localhost:5000',
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    webview.start()
