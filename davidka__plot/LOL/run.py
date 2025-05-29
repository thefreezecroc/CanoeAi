from app.routes import app
from stroke_detection import start_detection
from threading import Thread

if __name__ == "__main__":
    # Start BLE listener in background
    thread = Thread(target=start_detection, daemon=True)
    thread.start()

    # Start Flask web server
    app.run(debug=True)
