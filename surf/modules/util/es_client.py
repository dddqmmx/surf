import traceback

from elasticsearch import Elasticsearch


class ESClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.es_conn = None
        self.hosts = [{'host': 'www.dddqmmx.asia', 'port': 9200}]  # 默认配置
        self.username = None
        self.password = None
        self.minconn = 1
        self.maxconn = 10
        self.timeout = 30
        self.http_auth = None

    def __ensure_connection(self):
        if self.es_conn is None:
            self.createConnection()

    def createConnection(self):
        es_hosts = [
            {
                'host': host.get('host'),
                'port': host.get('port'),
                'scheme': 'http'  # 添加 scheme 参数
            } for host in self.hosts
        ]
        self.es_conn = Elasticsearch(
            hosts=es_hosts,
            http_auth=self.http_auth,
            maxsize=self.maxconn,
            max_retries=3,
            retry_on_timeout=True,
            timeout=self.timeout
        )

    def index(self, index, body, id=None):
        self.__ensure_connection()
        return self.es_conn.index(index=index, body=body, id=id)

    def get(self, index, id):
        self.__ensure_connection()
        return self.es_conn.get(index=index, id=id)

    def search(self, index, body):
        self.__ensure_connection()
        return self.es_conn.search(index=index, body=body)

    def update(self, index, id, body):
        self.__ensure_connection()
        return self.es_conn.update(index=index, id=id, body=body)

    def delete(self, index, id):
        self.__ensure_connection()
        return self.es_conn.delete(index=index, id=id)

    def delete_index(self, index):
        self.__ensure_connection()
        return self.es_conn.indices.delete(index=index)

    def bulk(self, actions):
        self.__ensure_connection()
        return self.es_conn.bulk(actions)

    def count(self, index, doc_type, body=None):
        self.__ensure_connection()
        return self.es_conn.count(index=index, doc_type=doc_type, body=body)

    def generator(self, data_list, bulk_type=None):
        # 往ES中插入数据的生成器
        # bulk_type: create-存在则不更新
        try:
            for item in data_list:
                if bulk_type:
                    yield {
                        "_op_type": bulk_type,
                        "_id": item["_id"],
                        "_source": item["_source"],
                        "_type": item["_type"],
                        "_index": item["_index"],
                    }
                else:
                    yield {
                        "_id": item["_id"],
                        "_source": item["_source"],
                        "_type": item["_type"],
                        "_index": item["_index"],
                    }
        except Exception as e:
            error_msg = f"Function generator error. Error:{e}\n{traceback.format_exc()}"
