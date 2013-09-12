# -*- coding: utf-8 -*- 
from flask import Blueprint, render_template, jsonify, request
from feedparser import parse
import setting

mod = Blueprint('test', __name__)


@mod.route("/douban")
def douban():
    book = parse(setting.DOUBAN_API_PATH + '/' + '11542537')
    return jsonify(book=book)

@mod.route("/json")
def json():
    return jsonify(status= 1, statusText = u'上传成功!', data = {'photoId' : 'tets', 'urls' : ['a']})

@mod.route("/testjson")
def testjson():
    data = request.data
    return render_template("test/json.html", data = data)

