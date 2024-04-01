from surf.modules.util.es_client import ESClient

# 创建 ESClient 实例
es_client = ESClient()

# # 创建文档
index_name = 'message'
# doc_body = {
#     'name': 'John Doe',
#     'age': 30,
#     'email': 'john.doe@example.com'
# }
# try:
#     create_response = es_client.index(index_name, doc_body, id=None)
#     print(f"Document created: {create_response['result']}")
# except Exception as e:
#     print(f"Error creating document: {e}")

# # 获取文档
# doc_id = create_response['_id']
# try:
#     get_response = es_client.get(index_name, doc_id)
#     print(f"Retrieved document: {get_response['_source']}")
# except Exception as e:
#     print(f"Error retrieving document: {e}")
#
# # 更新文档
# update_body = {
#     'doc': {
#         'age': 31
#     }
# }
# try:
#     update_response = es_client.update(index_name, doc_id, update_body)
#     print(f"Document updated: {update_response['result']}")
# except Exception as e:
#     print(f"Error updating document: {e}")
#
# 搜索文档
search_body = {
    'query': {
        'match_all': {}
    }
}
try:
    search_response = es_client.search(index_name, search_body)
    print(f"Search results: {search_response['hits']['hits'][0]['_source']}")
except Exception as e:
    print(f"Error searching documents: {e}")
#
# # 删除文档
# try:
#     delete_response = es_client.delete(index_name, doc_id)
#     print(f"Document deleted: {delete_response['result']}")
# except Exception as e:
#     print(f"Error deleting document: {e}")
#
# # 删除索引
# try:
#     delete_response = es_client.delete_index(index_name)
#     print(f"Index deleted: {delete_response}")
# except Exception as e:
#     print(f"Error deleting index: {e}")
