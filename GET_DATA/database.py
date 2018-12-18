import sys

import pymysql


class Database():
    def __init__(self):
        self.conn = None
        self.cur = None

    def connect(self):
        db_host = "gz-cdb-qdii0z2b.sql.tencentcdb.com"
        db_port = 61805
        db_user = "root"
        db_pass = 'Azslc123456'
        db_name = "ttrate"
        db_char = "utf8mb4"

        try:
            self.conn = pymysql.connect(host=db_host,port=db_port, user=db_user, passwd=db_pass, db=db_name,
                                        charset=db_char )
            self.cur = self.conn.cursor()
            print("Database connection succeeded!")
        except Exception as e:
            print(e)

    def get_all_content(self):
        #from all_city table
        query = ("select id , content_clean_tag_add_pos "
                 "from sa_article_content_done ")
        self.cur.execute(query)
        self.conn.commit()
        temp_list= self.cur.fetchall()
        # imdb_id_list = list(imdb_id_list)
        # temp_list = []
        # for item in imdb_id_list:
        #     temp_list.append(item[0])
        return temp_list

    def get_already_have_title(self):
        # from all_city table
        query = ("SELECT search_title "
                 "FROM {}".format(self.table_name))
        self.cur.execute(query)
        self.conn.commit()
        already_have_title_list = self.cur.fetchall()
        already_have_title_list = list(already_have_title_list)

        return already_have_title_list

    def insert_movie(self, *args):
        query = ("INSERT INTO {} "
                 "(search_title, result_title , search_year , url , description) "
                 "VALUES {};".format(self.table_name , args))
        self.cur.execute(query)
        self.conn.commit()

    def update_director(self, new_director , update_imdb_id):
        query = ("update {} set director = %s "
                 "where imdb_id  = %s;".format(self.table_name , new_director , update_imdb_id))
        self.cur.execute(query)
        self.conn.commit()

    def update_clean_content(self, clean_content , content_id):
        query = ("update sa_article_content_done set content_clean_tag = %s "
                 "where id  = %s;")
        self.cur.execute(query , (clean_content , content_id))
        self.conn.commit()

    def update_clean_content_pos(self, content , content_id):
        query = ("update sa_article_content_done set content_clean_tag_add_pos = %s "
                 "where id  = %s;")
        self.cur.execute(query , (content , content_id))
        self.conn.commit()

    def update_dict(self, my_dict, id):

        'update table set xxx = xxx , yyy= yyy where id = ???'
        temp_query = ''
        for key , value in my_dict.items():
            temp_query += key + '=' + str(value) + ','
        temp_query = temp_query[:-1]
        sql = " update sa_article_content_done set %s where id = %s" % (temp_query ,id)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            print("SQL error:", sys.exc_info()[1])

    def insert_dict(self, my_dict, table_name):
        data_values = "(" + "%s," * (len(my_dict)) + ")"
        data_values = data_values.replace(',)', ')')

        dbField = my_dict.keys()
        dataTuple = tuple(my_dict.values())
        dbField = str(tuple(dbField)).replace("'", '')
        sql = """ insert into %s %s values %s """ % (table_name, dbField, data_values)
        params = dataTuple
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except:
            print("SQL error:", sys.exc_info()[1])

    def close(self):
        self.cur.close()
        self.conn.close()


