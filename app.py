from flask import Flask
import os

app = Flask(__name__)

# ✅ Safe route (no crash)
@app.route("/")
def home():
    return "CodeMailer AI is running 🚀"

# ✅ Test route for your logic
@app.route("/test")
def test():
    try:
        import main
        main.run()
        return "Test executed successfully ✅"
    except Exception as e:
        return f"Error: {str(e)}", 500

# ✅ Only ONE main block
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)