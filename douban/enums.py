from enum import Enum


class SpiderNameEnum(Enum):
    # 影评爬虫
    movie_evaluation = 'movie_evaluation'
    # 影片爬虫
    movie = 'movie'


class RedisKeyEnum(Enum):
    # 分类电影的url地址集合
    movie_type_url = 'movie_type_url'
    movie_url_set = 'movie_url'
    # 已经爬取过的电影标签集合
    over_movie_tag_set = 'over_movie_tag_set'
    # 电影和类型对照 哈希
    movie_and_type_id = 'movie_and_type_id'
    # 已经爬取过的电影id哈希
    over_movie_id_hash_keys = 'over_movie_id_hash_keys'
    # 用于影评爬虫的电影id
    movie_id_hash_keys = 'movie_id_hash_keys'
    # 已经爬取过的影评id集合
    over_movie_comment_set = 'over_movie_comment_set'
    # 已经爬取过影评的豆瓣电影id
    over_comment_movie_id_set = 'over_comment_movie_id_set'
    # 每部电影开始爬取的页数哈希
    movie_comment_page_hash_keys = 'movie_comment_page'
