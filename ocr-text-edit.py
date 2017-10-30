#encoding: utf-8

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for
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
    d1 = {'名称':"东方财富信息股份有限公司",'纳税人识别号':'1234223432344234'}
    d2 = {'test':'12321323','test2':'e4457567687'}
    redis_store.hmset('OCR.INVOICE.20171010.JPG',d1)
    redis_store.hmset('OCR.XXXXXXX.20171012.JPG',d2)
    #读取redis方法
    result = redis_store.hgetall('OCR.INVOICE.20171010.JPG')
    result = json.dumps(result ,ensure_ascii=False)
    # return render_template("items_table.html", result = result)
    return redirect(url_for('getItems'))

@app.route('/items',methods=['GET','POST'])
@app.route('/items/<string:name>',methods=['GET','POST'])
def getItems(name=None):
    if not name:
        items = redis_store.keys()
        keyWord = request.values.get('keyWord') or ''
        print keyWord
        items = [x for x in items if x.startswith('OCR.') and keyWord.lower() in x.lower()]
        print items
        return render_template("items_table.html", items=items)
    else:
        if request.method == 'GET':
            kvs = redis_store.hgetall(name)
            # kvs = json.dumps(kvs).decode("unicode-escape")
            return render_template("item_detail.html", kvs=kvs, item_name=name)
        elif request.method == 'POST':
            type = request.values.get('type')
            key = request.values.get('key')
            value = request.values.get('value')
            if request.values.get('delete'):
                key = request.values.get('key')
                redis_store.hdel(name, key)
                return jsonify(msg='删除成功', code=200)
            print type, key, value
            if redis_store.hexists(name, key):
                print name, key, value
                redis_store.hset(name, key, value)
            else:
                if not request.values.get('origin'):
                    return jsonify(msg='找不到原值', code=400)
                with redis_store.pipeline() as pipe:
                    pipe.multi()
                    redis_store.hdel(name, request.values.get('origin'))
                    redis_store.hset(name, key, value)
                    pipe.execute()
            return jsonify(msg='修改成功',code=200)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
