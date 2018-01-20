from flask import Flask,render_template, request
import json, certifi, jsonify, ast
from elasticsearch import Elasticsearch
import numpy as np

ep = "https://search-twittmap2-wyrpney5f6kj5lgndhaysbbdhy.us-east-1.es.amazonaws.com"
es = Elasticsearch(hosts=[ep], port=443, use_ssl=True, verify_certs=True, ca_certs=certifi.where())

application = Flask(__name__)

@application.route('/', methods=['GET','POST'])
def map():
    if request.method == "POST": # When user choses from drop down
        global value
        value = request.form["Search"]
        tweets = es.search(index='twittmap', doc_type='tweets', size = 10000, body={"query":{"match":{"text": value}}})
        json_output=[]
        for doc in tweets['hits']['hits']:
            if 'user' in doc['_source']:
                tag={}
                tag['text']=doc['_source']['text']
                tag['user']=doc['_source']['user']
                tag['time']=doc['_source']['time']
                tag['lat']=doc['_source']['geo'][1]
                tag['lng']=doc['_source']['geo'][0]
                json_output.append(tag)
        return render_template('map.html', result=json_output, search=value) # Return search result
    else: # First page - Show all pins
        global value
        value = False
        tweets = es.search(index='twittmap', doc_type='tweets', size = 10000, body={"query": { "match_all": {}}})
        json_output=[]
        for doc in tweets['hits']['hits']:
            if 'user' in doc['_source']:
                tag={}
                tag['text']=doc['_source']['text']
                tag['user']=doc['_source']['user']
                tag['time']=doc['_source']['time']
                tag['lat']=doc['_source']['geo'][1]
                tag['lng']=doc['_source']['geo'][0]
                json_output.append(tag)
        return render_template('map.html', result=json_output, search="") # Return All pins

@application.route('/nearby', methods = ['POST'])
def nearby():
    if request.method == "POST": # Always...but removing this causes an issue...
        if value:
            data = request.form['data']
            print data
            data = ast.literal_eval(data) # data[0] will be latLng, and data[1] is search term
            tweets = es.search(index='twittmap', doc_type='tweets', size=10000,
                body={
                    "query": {
                        "bool" : {
                            "must" : {
                                "match":{
                                    "text": value
                                    }
                            },
                            "filter" : {
                                "geo_distance" : {
                                    "distance" : "1000km",
                                    "geo" : data
                                }
                            }
                        }
                    }
                })
            json_output=[]
            for doc in tweets['hits']['hits']:
                tag={}
                tag['text']=doc['_source']['text']
                tag['user']=doc['_source']['user']
                tag['time']=doc['_source']['time']
                tag['lat']=doc['_source']['geo'][1]
                tag['lng']=doc['_source']['geo'][0]
                json_output.append(tag)
            return json.dumps(json_output)
        else:
            data = request.form['data']
            data = ast.literal_eval(data) # data[0] will be latLng, and data[1] is search term
            tweets = es.search(index='twittmap', doc_type='tweets', size=10000,
                body={
                    "query" : {
                        "bool" : {
                            "must" : {
                                "match_all" : {}
                            },
                            "filter" : {
                                "geo_distance" : {
                                    "distance" : "1000km",
                                    "geo" : data
                                }
                            }
                        }
                    }
                })
            json_output=[]
            for doc in tweets['hits']['hits']:
                tag={}
                tag['text']=doc['_source']['text']
                tag['user']=doc['_source']['user']
                tag['time']=doc['_source']['time']
                tag['lat']=doc['_source']['geo'][1]
                tag['lng']=doc['_source']['geo'][0]
                json_output.append(tag)
            #print json.dumps(json_output)
            #return json.dumps({"a":json_output})
            return json.dumps(json_output)

if __name__ == '__main__':
    application.debug = True
    application.run()
