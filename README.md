# 代码功能

1. 爬取豆瓣分类页面下的所有影片
2. 爬取已知豆瓣影片id的所有短片:目前只爬取看过的短评

# 技术栈

1. python3.7
2. redis
3. scrapy
4. MySQL

# 代码说明

1. movie为影片爬虫
2. movie_evaluation为影评爬虫
3. aop.py为一些切面函数，目前包括计算函数运行时间的切面
4. db_config.py为数据库及非关系型数据库配置
5. enums.py存储一些爬虫name及redis的key
6. extension.py为计算爬取速率的扩展
7. utils.py包含一些预处理的函数
8. sql文件夹包含了数据库的初始化SQL
9. url_list.txt包含了一些豆瓣的数据地址
10. 配置文件中加入了随机ua，日志输出设置，休眠时间等配置
