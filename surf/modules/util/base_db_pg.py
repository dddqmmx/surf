import re

from psycopg2.pool import SimpleConnectionPool


class BaseDBPG(object):
    def __init__(self):
        self.table_clumns_dict = {}
        self.trans_conn = None
        self.trans_error_cb = None
        self.trans_cur = None

        self.timing_start = None
        self.timing_end = None

        self.schema = "public"
        self.setConnPool()

    def setConnPool(self):
        if not hasattr(self, "conn_pool") or not self.conn_pool:
            self.conn_pool = SimpleConnectionPool(
                minconn="1",
                maxconn="50",
                host='www.dddqmmx.asia',
                port='5432',
                database="surf",
                user='postgres',
                password='114514'
            )

    def get_Schema(self):
        if not hasattr(self, "schema"):
            return 'public'
        return self.schema

    def set_Schema(self, schema, conn):
        if not hasattr(conn, 'search_path_set') or not conn.search_path_set:
            self.schema = schema
            cur = conn.cursor()
            try:
                cur.execute("SET search_path TO " + schema)
                conn.commit()
            except Exception as e:
                conn.rollback()
            finally:
                cur.close()

    def getConn(self):
        conn = self.conn_pool.getconn()
        return conn

    def releaseConn(self, conn):
        self.conn_pool.putconn(conn)

    def closeAllConn(self):
        self.conn_pool.closeall()

    def debugSql(self, sql, params):
        if params:
            for param in params:
                sql = re.sub(r"%\w", "'%s'" % str(param), sql, count=1)
        print(sql)

    def formatSqlParams(self, sql, filters, re_str=None):
        re_str = re_str if re_str else r'{(\w*)}'
        field_list = re.compile(re_str).findall(sql)
        params = []
        for field in field_list:
            params.append(filters[field])
        sql = re.compile(re_str).sub("%s", sql)
        return sql, params

    def getClumnsByTable(self, table):
        if table not in self.table_clumns_dict:
            params = table.split(".") if '.' in table else [self.get_Schema(), table]
            sql = """
            SELECT column_name FROM information_schema.columns WHERE table_schema = %s AND table_name = %s
            """
            result = self.query(sql, params, debug=True)
            column = [item['column_name'] for item in result]
            self.table_clumns_dict[table] = column
        return self.table_clumns_dict[table]

    def slimSql(self, sql):
        sql = re.sub('\n', ' ', sql)
        sql = re.sub(' +', ' ', sql)
        return sql

    # 查询
    def query(self, sql, params=None, keys=None, debug=False):
        """
        查询

        :param sql: sql语句
        :param params: 参数
        :param keys: 不用传
        :param debug: 看sql语句的
        :return: 结果
        """
        if debug:
            self.debugSql(sql, params)
        conn = self.getConn()
        cur = conn.cursor()
        try:
            sql = self.slimSql(sql)
            cur.execute(sql, params)
            res = []
            try:
                res = cur.fetchall()
            except Exception as e:
                if 'no results to fetch' in str(e):
                    res = []
                    keys = ['']
            if not keys:
                des = cur.description
                keys = [x[0] for x in des]
            rows = []
            for row in res:
                rows.append(dict(zip(keys, row)))
            conn.commit()
            return rows
        except Exception as e:
            conn.rollback()
            print(str(e))
            return []
        finally:
            if cur:
                cur.close()
                self.releaseConn(conn)

    def queryFormat(self, sql, keys=None, filters=None, re_str=None, debug=False):
        sql, params = self.formatSqlParams(sql, filters, re_str)
        if debug:
            self.debugSql(sql, params)
        return self.query(sql, params, keys, debug=debug)

    def formateOrderLimit(self, filters):
        sql = ''
        if 'orderField' in filters and "orderMode" in filters:
            if filters['orderField'] and filters['orderMode']:
                order_con = " ORDER BY %s %s" % (filters['orderField'], filters['orderMode'])
                sql += order_con

        # 当前页码和页面长度限制
        if 'pageSize' in filters and 'pageIndex' in filters:
            limit = int(filters['pageSize'])
            offset = (int(filters['pageIndex']) - 1) * limit
            sql += " OFFSET %s LIMIT %S" % (offset, limit)
        return sql

    def queryPage(self, filters, sql, params=None, keys=None, debug=False):
        list_sql = sql + self.formatSqlParams(filters)
        count_sql = "SELECT COUNT(1) AS total_counts FROM (" + sql + ") AS TMP_COUNT"
        list = self.query(list_sql, params, keys=keys, debug=debug)
        count = self.query(count_sql, params)[0]['total_counts']
        result = {
            'totalCounts': count,
            "list": list
        }
        return result

    def getUpdatesqlParams(self, table, filters, primary=None, return_id=False, return_id_clumn='ID'):
        primary = 'id' if not primary else primary
        clumns = self.getClumnsByTable(table)
        upd_arr = []
        params = []
        for key, values in filters.items():
            if key not in clumns:
                # 防止注入问题
                continue
            if key != primary:
                upd_arr.append(key + " = %s")
                params.append(values)
        field_values = ', '.join(upd_arr)
        if return_id_clumn != 'ID' and return_id_clumn not in clumns:
            return_id_clumn = 'ID'
        return_id_str = "RETURNING %s" % return_id_clumn if return_id else ''
        params += [filters[primary]]

        sql = f"""
        UPDATE {table} SET {field_values}
        WHERE {primary} = %s
        {return_id_str}
        """
        return sql, params

    def update(self, table, filters, primary=None, debug=False, return_id=False, return_id_clumn='ID'):
        if type(filters) == type([]):
            return self.updateBat(table, filters, primary, debug, return_id, return_id_clumn)
        elif type(filters) == type({}):
            return self.updateSingel(table, filters, primary, debug, return_id, return_id_clumn)
        else:
            print("Fa Q")
            return False

    def updateSingel(self, table, filters, primary=None, debug=False, return_id=False, return_id_clumn='ID'):
        conn = self.getConn()
        cur = conn.cursor()
        try:
            sql, params = self.getUpdatesqlParams(table, filters, primary, return_id, return_id_clumn)
            if debug:
                self.debugSql(sql, params)
            sql = self.slimSql(sql)
            cur.execute(sql, params)
            result = cur.fetchone()[0] if return_id else True
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(str(e))
            return False
        finally:
            if cur:
                cur.close()
                self.releaseConn(conn)

    def updateBat(self, table, filters, primary=None, debug=False, return_id=False, return_id_clumn='ID'):
        ids = []
        conn = self.getConn()
        cur = conn.cursor()
        try:
            for sin_filter in filters:
                sql, params = self.getUpdatesqlParams(table, sin_filter, primary, return_id, return_id_clumn)
                if debug:
                    self.debugSql(sql, params)
                sql = self.slimSql(sql)
                cur.execute(sql, params)
                if return_id:
                    id = cur.fetchone()[0]
                    ids.append(id)
            result = cur.fetchone()[0] if return_id else True
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(str(e))
            return False
        finally:
            if cur:
                cur.close()
                self.releaseConn(conn)

    def delKeyByClumns(self, filters, clumns, table):
        del_keys = []
        for k, v in filters.items():
            if k not in clumns:
                del_keys.append(k)
                del filters[k]
        if len(del_keys) > 0:
            print(del_keys)
        return filters

    def getInsertSqlParams(self, table, filters, return_id=False, return_id_clumn='ID'):
        clumns = self.getClumnsByTable(table)
        filters = self.delKeyByClumns(filters, clumns, table)
        params = list(filters.values())
        values = ['%s'] * len(params)
        if return_id_clumn != 'ID' and return_id_clumn not in clumns:
            return_id_clumn = 'ID'
        return_id_str = "RETURNING %s" % return_id_clumn if return_id else ''
        sql = f"""
        INSERT INTO {table} ({', '.join(filters.keys())}) VALUES ({', '.join(values)}) {return_id_str}
        """
        return sql, params

    def insert(self, table, filters, debug=False, return_id=False, return_id_clumn='ID'):
        if type(filters) == type([]):
            return self.insertBat(table, filters, debug, return_id, return_id_clumn)
        elif type(filters) == type({}):
            return self.insertSingel(table, filters, debug, return_id, return_id_clumn)
        else:
            print("Fa Q")
            return False

    def insertSingel(self, table, filters, debug=False, return_id=False, return_id_clumn='ID'):
        conn = self.getConn()
        cur = conn.cursor()
        try:
            sql, params = self.getInsertSqlParams(table, filters, return_id=return_id, return_id_clumn=return_id_clumn)
            if debug:
                self.debugSql(sql, params)
            sql = self.slimSql(sql)
            cur.execute(sql, params)
            result = cur.fetchone()[0] if return_id else True
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(str(e))
            return False
        finally:
            if cur:
                cur.close()
                self.releaseConn(conn)

    def insertBat(self, table, filters, debug=False, return_id=False, return_id_clumn='ID'):
        ids = []
        conn = self.getConn()
        cur = conn.cursor()
        try:
            for sin_filter in filters:
                sql, params = self.getInsertSqlParams(table, sin_filter, return_id=return_id,
                                                      return_id_clumn=return_id_clumn)
                if debug:
                    self.debugSql(sql, params)
                sql = self.slimSql(sql)
                print(params)
                cur.execute(sql, params)
                if return_id:
                    id = cur.fetchone()[0]
                    ids.append(id)
            result = cur.fetchone()[0] if return_id else True
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(str(e))
            return False
        finally:
            if cur:
                cur.close()
                self.releaseConn(conn)

    def save(self, table, filters, primary=None, debug=False, return_id=False, return_id_clumn='ID'):
        primary = 'id' if not primary else primary
        if type(filters) == type([]):
            return self.saveBat(table, filters, primary, debug=debug, return_id=return_id, return_id_clumn=return_id_clumn)
        elif type(filters) == type({}):
            return self.saveSingel(table, filters, primary, debug=debug, return_id=return_id, return_id_clumn=return_id_clumn)
        else:
            print("Fa Q")
            return False

    def saveSingel(self, table, filters, primary=None, debug=False, return_id=False, return_id_clumn='ID'):
        primary = 'id' if not primary else primary
        if primary in filters:
            return self.update(table, filters, primary, debug=debug, return_id = return_id, return_id_clumn=return_id_clumn)
        else:
            return  self.insert(table, filters, debug=debug, return_id=return_id,return_id_clumn=return_id_clumn)

    def saveBat(self, table, filters, primary=None, debug=False, return_id=False, return_id_clumn='ID'):
        primary = 'id' if not primary else primary
        upd_arr = []
        ins_arr = []
        for sin_filter in filters:
            if primary in sin_filter:
                upd_arr.append(sin_filter)
            else:
                ins_arr.append(sin_filter)
        ids = []
        if len(ins_arr) > 0:
            return self.insertBat(table, ins_arr,debug=debug, return_id=return_id, return_id_clumn=return_id_clumn)
        if len(upd_arr) > 0:
            self.updateBat(table, upd_arr,debug=debug, return_id=return_id, return_id_clumn=return_id_clumn)



if __name__ == "__main__":
    pg = BaseDBPG()
    sql = """
    SELECT * FROM public.user
    """
    res = pg.query(sql)
    for item in res:
        print(item['uuid'])
        print(item['nickname'])
        print(item['public_key'])
        print()
        print()
    # print(res)
    # print("")
    # print("")
    # filters = {
    #     "uuid": '1',
    #     "nickname": '1',
    #     "public_key": '1'
    # }
    # pg.save('public.user', filters, primary='uuid')
    # print(pg.query(sql))
    print("")
    print("")
    filters = [
        {
            "nickname": 'dddqmmx',
            "public_key": 'tmd弄个自增长id啊混蛋'
        },
        {
            "nickname": 'Van Darkholme',
            "public_key": 'FaQ'
        },
        {
            "nickname": '七海娜娜米',
            "public_key": '114514'
        },
        {
            "nickname": '白上吹雪',
            "public_key": '1919810'
        },
        {
            "nickname": '我就是傻逼',
            "public_key": '131331'
        }
    ]
    # res = pg.save('public.user', filters, debug=True)
    # print(res)
