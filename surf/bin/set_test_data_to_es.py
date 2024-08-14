# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/22 17:11
File Name       : set_test_data_to_es.py
Last Edit Time  : 
"""
import copy
import datetime
import time
import uuid

from elasticsearch import Elasticsearch, helpers

from surf.appsGlobal import CHAT_TEMP
from surf.modules.util.es_client import ESClient

es_cluster = ["surf.dddqmmx.asia:9200"]
ec = ESClient()
es = Elasticsearch(es_cluster)

new_es_data = []
d1 = copy.deepcopy(CHAT_TEMP)
d2 = copy.deepcopy(CHAT_TEMP)
d3 = copy.deepcopy(CHAT_TEMP)
d4 = copy.deepcopy(CHAT_TEMP)
d5 = copy.deepcopy(CHAT_TEMP)

d1["_id"] = uuid.uuid4()
d1["_source"]["chat_id"] = d1["_id"]
d1["_source"]["type"] = "text"
d1["_source"]["content"] = "Hello! How are you today"
d1["_source"]["user_id"] = "e2cfa16b-c7a3-46f0-9995-22e2ae333e3e"
d1["_source"]["chat_time"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

time.sleep(1)

d2["_id"] = uuid.uuid4()
d2["_source"]["chat_id"] = d2["_id"]
d2["_source"]["type"] = "text"
d2["_source"]["content"] = "ur a giant pussy"
d2["_source"]["user_id"] = "02c9aba4-44a0-4ddf-8cf2-70c6e5e554d7"
d2["_source"]["chat_time"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

time.sleep(1)

d3["_id"] = uuid.uuid4()
d3["_source"]["chat_id"] = d3["_id"]
d3["_source"]["type"] = "img"
d3["_source"]["content"] = "idk how stage this fucking image,maybe url or data?	"
d3["_source"]["user_id"] = "e2cfa16b-c7a3-46f0-9995-22e2ae333e3e"
d3["_source"]["chat_time"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

time.sleep(1)

d4["_id"] = uuid.uuid4()
d4["_source"]["chat_id"] = d4["_id"]
d4["_source"]["type"] = "text"
d4["_source"]["content"] = "The only pussy I know is your daughter's"
d4["_source"]["user_id"] = "02c9aba4-44a0-4ddf-8cf2-70c6e5e554d7"
d4["_source"]["chat_time"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

time.sleep(1)

d5["_id"] = uuid.uuid4()
d5["_source"]["chat_id"] = d5["_id"]
d5["_source"]["type"] = "text"
d5["_source"]["content"] = "if u touch her ill fucking end u	"
d5["_source"]["user_id"] = "e2cfa16b-c7a3-46f0-9995-22e2ae333e3e"
d5["_source"]["chat_time"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

new_es_data.append(d1)
new_es_data.append(d2)
new_es_data.append(d3)
new_es_data.append(d4)
new_es_data.append(d5)
for data in new_es_data:
    data["_index"] = "chat_message"
    data["_source"]["channel_id"] = "aa6cd21b-7080-4e65-9059-8a6a8c303cbb"

count = helpers.bulk(
                    es,
                    ec.generator(new_es_data),
                    raise_on_exception=False,
                    raise_on_error=False
                )