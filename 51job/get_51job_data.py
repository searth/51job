# ==================================
# --*-- coding: utf-8 --*--
# @Time    : 2021-03-02
# @FileName: get_51job_data.py
# @Software: Sublime Text 3
# ==================================


import re
import time
import copy
import requests
import json
import threading
from lxml import etree
import pandas as pd


class JobSpider:
    def __init__(self):
    	# 设置基础网页形式、浏览器请求头，输入查询关键字
        self.base_url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,%s,2,%s.html'
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.13 Safari/537.36'}
        self.keyword = input('请输入关键字：')
        self.starttime = time.time()
        self.sumdata = []

    def tatal_url(self):
    	# 补全网页
        url = self.base_url % (self.keyword, str(1))
        response = requests.get(url=url, headers=self.headers)
        # 转换为Element对象
        tree = etree.HTML(response.content.decode('gbk'))
        # 提取一共有多少页
        text = tree.xpath('//script[@type="text/javascript"]/text()')
        qwq = "".join(text)
        dic = json.loads(qwq[29:])
        number = dic['total_page']
        number = int(''.join(number))
        print('%s职位共有%d页' % (self.keyword, number))
        return number

    def detail_url(self, number):

        """
        1、解析每一页职位详情页的 url
        2、特殊情况一：如果有前程无忧自己公司的职位招聘信息掺杂在里面，他的详情页结构和普通的也不一样，页面编码也有差别。
           页面示例：https://51rz.51job.com/job.html?jobid=115980058
           页面真实数据请求地址类似于：https://coapi.51job.com/job_detail.php?jsoncallback=&key=&sign=params={"jobid":""}
           请求地址中的各参数值通过 js 加密：https://js.51jobcdn.com/in/js/2018/coapi/coapi.min.js
           (如果不用selenium，如何锁定这个网址，持疑，待解决☆☆☆)
        3、特殊情况二：部分公司有自己的专属页面，此类页面的结构也不同于普通页面(和上面那个一起解决☆☆☆)
           页面示例：http://dali.51ideal.com/jobdetail.html?jobid=121746338
        4、为了规范化，本次爬取将去掉这部分特殊页面，仅爬取 url 带有 jobs.51job.com 的数据
        """

        for num in range(1, number+1):
            url = self.base_url % (self.keyword, str(num))
            response = requests.get(url=url, headers=self.headers)
            tree = etree.HTML(response.content.decode('gbk'))
            text1 = tree.xpath('//script[@type="text/javascript"]/text()')
            qwq1 = "".join(text1)
            dic1 = json.loads(qwq1[29:])
            detail_url1 = []
            k = dic1['engine_search_result']
            for j in k:
            	detail_url1.append(j['job_href'])

            """
            深拷贝一个 url 列表，如果有连续的不满足要求的链接，若直接在原列表里面删除，
            则会漏掉一些链接，因为每次删除后的索引已改变，因此在原列表中提取不符合元素
            后，在深拷贝的列表里面进行删除。最后深拷贝的列表里面的元素均符合要求。
            """

            detail_url2 = copy.deepcopy(detail_url1)
            for url in detail_url1:
                if 'jobs.51job.com' not in url:
                    detail_url2.remove(url)
            self.parse_data(detail_url2)

            print('第%d页数据爬取完毕！' % num)
            time.sleep(2)
            if num > 1:
            	break
        print('所有数据爬取完毕！')
        print("耗时：", time.time() - self.starttime)
        deal(self.sumdata,self.keyword)

    def parse_data(self, urls):

        """
        position:            职位
        wages:               工资
        region:              地区
        experience:          经验
        education:           学历
        need_people:         招聘人数
        publish_date:        发布时间
        english:             英语要求
        welfare_tags:        福利标签
        job_information:     职位信息
        work_address:        上班地址
        company_name:        公司名称
        company_nature:      公司性质
        company_scale:       公司规模
        company_industry:    公司行业
        company_information: 公司信息
        """


        for url in urls:
	        response = requests.get(url=url, headers=self.headers)
	        try:
	            text = response.content.decode('gbk')
	        except UnicodeDecodeError:
	            return
	        tree = etree.HTML(text)

	        """
	        提取内容时使用 join 方法将列表转为字符串，而不是直接使用索引取值，
	        这样做的好处是遇到某些没有的信息直接留空而不会报错
	        """

	        position = ''.join(tree.xpath("//div[@class='cn']/h1/text()"))
	        wages = ''.join(tree.xpath("//div[@class='cn']/strong/text()"))

	        # 经验、学历、招聘人数、发布时间等信息都在一个标签里面，逐一使用列表解析式提取
	        content = tree.xpath("//div[@class='cn']/p[2]/text()")
	        # 去空格
	        content = [i.strip() for i in content]
	        if content:
	            region = content[0]
	        else:
	            region = ''
	        experience = ''.join([i for i in content if '经验' in i])
	        education = ''.join([i for i in content if i in '本科大专应届生在校生硕士'])
	        need_people = ''.join([i for i in content if '招' in i])
	        publish_date = ''.join([i for i in content if '发布' in i])
	        english = ''.join([i for i in content if '英语' in i])

	        # 词语用逗号分隔，第一个最后一个都是换行符
	        welfare_tags = ','.join(tree.xpath("//div[@class='jtag']/div//text()")[1:-2])
	        job_information = ''.join(tree.xpath("//div[@class='bmsg job_msg inbox']/p//text()")).replace(' ', '')
	        work_address = ''.join(tree.xpath("//div[@class='bmsg inbox']/p//text()"))
	        company_name = ''.join(tree.xpath("//div[@class='tCompany_sidebar']/div[1]/div[1]/a/p/text()"))
	        company_nature = ''.join(tree.xpath("//div[@class='tCompany_sidebar']/div[1]/div[2]/p[1]//text()"))
	        company_scale = ''.join(tree.xpath("//div[@class='tCompany_sidebar']/div[1]/div[2]/p[2]//text()"))
	        company_industry = ''.join(tree.xpath("//div[@class='tCompany_sidebar']/div[1]/div[2]/p[3]/@title"))
	        company_information = ''.join(tree.xpath("//div[@class='tmsg inbox']/text()"))

	        job_data = [position, wages, region, experience, education, need_people, publish_date,
	                    english, welfare_tags, job_information, work_address, company_name,
	                    company_nature, company_scale, company_industry, company_information]
	        self.sumdata.append(job_data)



def deal(data,keyword):
	index = ['职位','工资','地区','经验','学历','招聘人数','发布时间','英语要求','福利标签','职位信息','上班地址','公司名称','公司性质','公司规模','公司行业','公司信息']
	df = pd.DataFrame(data,columns = index)
	df.to_excel(keyword+'.xlsx')



if __name__ == '__main__':
    spider = JobSpider()
    page_number = spider.tatal_url()
    spider.detail_url(page_number)