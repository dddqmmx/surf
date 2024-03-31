# 连接ES
from surf.modules.util.es_utils import ESUtils

es_util = ESUtils(hosts=["http://192.168.6.130:9200"])

# 创建索引
index_name = "test_index"
index_mapping = {
    "mappings": {
        "properties": {
            "name": {"type": "text"},
            "age": {"type": "integer"}
        }
    }
}
es_util.create_index(index_name, index_mapping)

# 插入数据
doc = {
    "name": "Alice",
    "age": 25
}
es_util.insert_data(index_name, doc)

# 查询数据
query = {
    "query": {
        "match_all": {}
    }
}
result = es_util.search_data(index_name, query)

# 检查查询结果是否为空
if result["hits"]["hits"]:
    for hit in result["hits"]["hits"]:
        print(hit["_source"])

    # 更新数据
    doc_id = result["hits"]["hits"][0]["_id"]
    update_body = {"age": 26}
    es_util.update_data(index_name, doc_id, update_body)
else:
    print("没有找到任何文档")

# 更新数据
doc_id = result["hits"]["hits"][0]["_id"]
update_body = {"age": 26}
es_util.update_data(index_name, doc_id, update_body)

# 删除数据
es_util.delete_data(index_name, doc_id)

# 删除索引
es_util.delete_index(index_name)