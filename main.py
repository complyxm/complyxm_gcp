from flask import Flask, render_template
import complyxmmain

# appをインスタンスとして立てる
app = Flask(__name__)

@app.route('/')
def hello():
     data = complyxmmain.printResult()
     # print(data)
     return render_template('hello.html',data=data)

if __name__ == '__main__':
    app.run()