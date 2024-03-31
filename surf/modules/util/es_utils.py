from elasticsearch import Elasticsearch

class ESUtils:
    def __init__(self, hosts):
        """
        初始化ES连接
        :param hosts: ES服务器地址,如["http://localhost:9200"]
        """
        self.es = Elasticsearch(hosts=hosts)

    def create_index(self, index_name, body=None):
        """
        创建索引
        :param index_name: 索引名称
        :param body: 索引映射配置
        :return:
        """
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=body)
            print(f"成功创建索引 {index_name}")
        else:
            print(f"索引 {index_name} 已存在")

    def delete_index(self, index_name):
        """
        删除索引
        :param index_name: 索引名称
        :return:
        """
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
            print(f"成功删除索引 {index_name}")
        else:
            print(f"索引 {index_name} 不存在")

    def insert_data(self, index_name, body):
        """
        插入数据
        :param index_name: 索引名称
        :param body: 数据
        :return:
        """
        result = self.es.index(index=index_name, body=body)
        print(f"插入数据成功, id={result['_id']}")

    def search_data(self, index_name, body):
        """
        查询数据
        :param index_name: 索引名称
        :param body: 查询条件
        :return:
        """
        result = self.es.search(index=index_name, body=body)
        return result

    def update_data(self, index_name, doc_id, body):
        """
        更新数据
        :param index_name: 索引名称
        :param doc_id: 文档id
        :param body: 更新内容
        :return:
        """
        result = self.es.update(index=index_name, id=doc_id, body={"doc": body})
        print(f"更新数据成功, id={result['_id']}")

    def delete_data(self, index_name, doc_id):
        """
        删除数据
        :param index_name: 索引名称
        :param doc_id: 文档id
        :return:
        """
        result = self.es.delete(index=index_name, id=doc_id)
        print(f"删除数据成功, id={result['_id']}")