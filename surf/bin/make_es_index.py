# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/22 16:44
File Name       : make_es_index.py
Last Edit Time  : 
"""

from elasticsearch import Elasticsearch

es_cluster = ["www.dddqmmx.asia:9200"]
es = Elasticsearch(es_cluster)

index_name = "chat_message"
body = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2
    },
    "mappings": {
        "properties": {
            "chat_id": {
                "type": "keyword"
            },
            "type": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "content": {
                "type": "text"
            },
            "user_id": {
                "type": "keyword"
            },
            "chat_time": {
                "type": "date",
                "format": "yyyy-MM-dd'T'HH:mm:ss'Z'"
            }
        }
    },
    "aliases": {
        "alias_chat_message": {}
    }
}

es.indices.create(index=index_name, body=body)
