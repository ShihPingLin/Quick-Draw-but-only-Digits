import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'digits_recognition'))

from back_end.server import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 80)))