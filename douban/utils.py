import logging
import redis
from mysql.connector import pooling
from douban.db_config import MYSQL_CONFIG, REDIS_CONFIG
from douban.enums import RedisKeyEnum
from douban.aop import consume_time


class MysqlManager(object):
    def __init__(self):
        self.mcp = pooling.MySQLConnectionPool(**MYSQL_CONFIG)

    def execute_dml(self, sql_str, *args):
        cnx = None
        try:
            cnx = self.mcp.get_connection()
            cursor = cnx.cursor()
            cursor.execute(sql_str, args)
            cursor.close()
            cnx.commit()
        except Exception as e:
            logging.log(logging.ERROR, e)
            raise e
        finally:
            if cnx:
                cnx.close()

    def execute_query(self, sql_str, *args):
        cnx = None
        try:
            cnx = self.mcp.get_connection()
            cursor = cnx.cursor()
            cursor.execute(sql_str, args)
            result_set = cursor.fetchall()
            cursor.close()
            return result_set
        except Exception as e:
            logging.log(logging.ERROR, "args:{},err:{}".format(args, e))
        finally:
            if cnx:
                cnx.close()

    def test(self):
        conn = self.mcp.get_connection()
        cur = conn.cursor()
        sql = "select count(*) from movie"
        r = cur.execute(sql)
        r = cur.fetchall()
        print(r)
        cur.close()
        conn.close()


class RedisManager(object):
    def __init__(self):
        self.rdp = redis.ConnectionPool(**REDIS_CONFIG)
        self.rdc = redis.StrictRedis(connection_pool=self.rdp)

    def test(self):
        self.rdc.set("test", "hhhhhhhhhh", 10)
        print(self.rdc.get("test"))


def put_movie_url_to_redis():
    movie_url = 'https://movie.douban.com/j/chart/top_list?type={}&interval_id={}&start=0&limit={}'
    rdc = RedisManager().rdc
    for i in range(1, 32):
        type_set = rdc.hkeys(i)
        for type_interval in type_set:
            rdc.sadd('movie_url', movie_url.format(i, type_interval, rdc.hget(i, type_interval)))


def put_type_id_to_redis():
    mcp = MysqlManager()
    rdc = RedisManager().rdc
    query_sql = 'select id,type_name from movie_type where douban_type_id = %s;'
    for i in range(1, 32):
        if i == 9 or i == 21:
            continue
        type_id = mcp.execute_query(query_sql, i)[0]
        rdc.hset("type_name_and_id", type_id[1], type_id[0])


def format_date(date_str):
    if date_str is None or len(date_str) == 0:
        return '1900-01-01'
    if len(date_str.split('-')) < 3:
        return "{}-01-01".format(date_str)
    return date_str


def put_movie_ids_to_redis():
    rdc = RedisManager().rdc
    mcp = MysqlManager()
    query_sql = 'select id,douban_movie_id from movie order by id desc ;'
    id_set = mcp.execute_query(query_sql)
    pipe = rdc.pipeline()
    for id_result in id_set:
        pipe.hset(RedisKeyEnum.movie_id_hash_keys.value, id_result[1], id_result[0])
    pipe.execute()


if __name__ == '__main__':
    put_movie_ids_to_redis()
