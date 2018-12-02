create database douban;
create table movie
(
  id              bigint       not null auto_increment,
  score           float        not null comment '评分',
  title           varchar(254) not null comment '标题',
  url             varchar(254) not null comment '详情页链接',
  directors       text comment '导演表',
  actors          text comment '演员表',
  cover_url       varchar(254) comment '封面',
  douban_movie_id bigint       not null comment '豆瓣电影id',
  create_time     timestamp    null default current_timestamp,
  update_time     timestamp    null default current_timestamp on update current_timestamp,
  primary key (id),
  index (title),
  unique key (douban_movie_id)
) engine = innodb comment '影片表';

create table movie_evaluation
(
  id                bigint    not null auto_increment,
  movie_id          bigint    not null,
  user              varchar(254)   default '' comment '评价人',
  already_watched   int       not null comment '是否已看',
  star              int       not null comment '评分',
  douban_comment_id bigint    not null comment '豆瓣存储的评论id',
  comment_content   text      not null comment '评论内容',
  comment_time      datetime  not null comment '评论时间',
  support_count     int            default 0 comment '有用数',
  create_time       timestamp null default current_timestamp,
  update_time       timestamp null default current_timestamp on update current_timestamp,
  primary key (id),
  foreign key (movie_id) references movie (id),
  unique key (douban_comment_id)
) engine = innodb comment '影评表';


create table movie_type
(
  id             bigint      not null auto_increment,
  type_name      varchar(64) not null comment '类名',
  count          int         not null comment '类别包含的电影数量',
  douban_type_id int         not null comment '豆瓣的类别id',
  create_time    timestamp   null default current_timestamp,
  update_time    timestamp   null default current_timestamp on update current_timestamp,
  primary key (id),
  index (type_name)
) engine = innodb comment '电影分类表';

create table movie_and_type
(
  id            bigint    not null auto_increment,
  movie_id      bigint    not null,
  create_time   timestamp null default current_timestamp,
  update_time   timestamp null default current_timestamp on update current_timestamp,
  movie_type_id bigint    not null,
  primary key (id),
  foreign key (movie_id) references movie (id),
  foreign key (movie_type_id) references movie_type (id)
) engine = innodb comment '电影-分类关系表';



