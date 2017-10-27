#encoding: utf-8

from flask import Flask
from flask import render_template
from flask import request
from flask.ext.redis import FlaskRedis
import json

app = Flask(__name__)
app.config.from_pyfile("config.py")
redis_store = FlaskRedis(app)
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

@app.route('/')
def hello_world():
    #写入redis方法
    d = {'名称':"东方财富信息股份有限公司",'纳税人识别号':'1234223432344234'}
    redis_store.hmset('OCR.INVOICE.20171010.JPG',d)
    #读取redis方法
    result = redis_store.hgetall('OCR.INVOICE.20171010.JPG')
    result = json.dumps(result ,ensure_ascii=False)
    return render_template("items_table.html", result = result)

@app.route('/items')
@app.route('/items/<string:name>')
def getItems(name=None):
    if not name:
        items = redis_store.keys()
        print items
        items = [x for x in items if x.startswith('OCR.')]
        items = [x for x in items if x.startswith('OCR.')]
        return render_template("items_table.html", items=items)
    else:
        print name
        kvs = redis_store.hgetall(name)
        # kvs = json.dumps(kvs).decode("unicode-escape")
        return render_template("item_detail.html", kvs=kvs, item_name=name)
if __name__ == '__main__':
    app.run()
