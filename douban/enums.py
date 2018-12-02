from enum import Enum


class SpiderNameEnum(Enum):
    movie_evaluation = 'movie_evaluation'
    movie = 'movie'


class RedisKeyEnum(Enum):
    movie_type_url = 'movie_type_url'
    movie_url_set = 'movie_url'
    over_movie_tag_set = 'over_movie_tag_set'
    movie_and_type_id = 'movie_and_type_id'
    over_movie_id_hash_keys = 'over_movie_id_hash_keys'
    # 用于影评爬虫的电影id
    movie_id_hash_keys = 'movie_id_hash_keys'
    over_movie_comment_set = 'over_movie_comment_set'
    over_comment_movie_id_set = 'over_comment_movie_id_set'
