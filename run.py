# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True 方便我们在开发时看到报错信息
    app.run(debug=True, port=5000)