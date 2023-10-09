from bs4 import BeautifulSoup #解析网页，获取数据
import re #正则表达式，进行文字匹配
import urllib.request,urllib.error  #制定url，获取网页数据
import xlwt  #进行excel操作
import sqlite3  #进行SQLite数据库操作

def main():
    baseurl = "https://movie.douban.com/top250?start="
    #爬取网页
    datalist = getData(baseurl)
    #保存数据
    dbpath = "douban250.db"
    saveData_db(datalist,dbpath)

#电影详情链接的规则
# r 忽视所有的特殊符号  <a href=" 所有的链接前面一串都相同  (.*) .表示0个 *表示多个 0个到多个字符 ? 0次或者多次  "> 后面的
findLink = re.compile(r'<a href="(.*?)">')  # compile创建正则表达式对象，表示规则(字符串模式)
#封面图片
findImgSrc = re.compile(r'<img.*src="(.*?)".*>',re.S) # re.S 忽略换行符
#电影名称
findTitle = re.compile(r'<span class="title">(.*)</span>')
#评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>') # \d表示数字 * 多个
#概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#电影详细内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

#爬取网页
def getData(baseurl):
    datalist = [] # 获取地址中的数据列表，并返回
    for i in range(0,10): # 调用获取页面信息的函数10次，一次25条
        url = baseurl + str(i*25)
        html = askURL(url) # 保存获取到的网页源码
        # 2.逐一解析数据
        soup = BeautifulSoup(html,"html.parser") # html.parser网页解析器
        # find_all()是按照一定的标准，将符合要求的字符串一次性查找出来形成列表
        for item in soup.find_all('div',class_="item"):  # class后的 _ 表示属性值
            #print(item)
            data = [] # 保存一部电影的所有信息
            item = str(item) # 将其转为字符串
            # 提取超链接 re库用来通过正则表达式找到指定的字符串 findLink是自定义的全局变量
            Link = re.findall(findLink,item)[0] # [0]第一个
            data.append(Link) # 将连接追加到列表中

            ImgSrc = re.findall(findImgSrc,item)[0]
            data.append(ImgSrc)

            Title = re.findall(findTitle,item) # 片名可能只有一个中文名没有外文名
            if len(Title)==2: # 判断有几个titles
                ctitle = Title[0] # 添加中文名
                data.append(ctitle)
                otitle = Title[1].replace("/","") # 去掉/
                data.append(otitle) # 添加外文名
            else:
                data.append(Title[0])
                data.append(' ') # 第二个留空

            Rating = re.findall(findRating,item)[0]
            data.append(Rating) # 添加评分

            Judge = re.findall(findJudge,item)[0]
            data.append(Judge) # 添加人数

            Inq = re.findall(findInq,item)
            if len(Inq) !=0: # 有概述
                Inq = Inq[0].replace("。","") # 替换。
                data.append(Inq)
            else:  # 没有概述
                data.append(" ")

            Bd = re.findall(findBd,item)[0]
            # 将bd中的 <br(\s+)?/>(\s+)? 替换
            Bd = re.sub('<br(\s+)?/>(\s+)?'," ",Bd)
            data.append(Bd.strip()) # strip去掉前后空格

            datalist.append(data)    #把处理好的一个电影信息存储到datalist中
    #解析网页
    return datalist

#获取指定一个网页内容
def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.116 Safari/537.36"
    } #伪装成网页的形式，请求网页信息
    request = urllib.request.Request(url,headers=head)
    html = "" # 存放到html中
    try: # 防止出现意外
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")  # 读取response
        #print(html)
    except urllib.error.URLError as e:  # 捕获404 500 等浏览器错误
        if hasattr(e,"code"):  #将其输出
            print(e.code)
        if hasattr(e,"reason"):  # 输出没有捕获成功的原因
            print(e.reason)
    return html
#保存数据
def saveData(datalist,savepath):
    print("save....")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)  # style_compression样式压缩效果
    sheet = book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True) #cell_overwrite_ok单元格覆盖
    col = ("电影详情链接","封面链接","影片中文名","影片外国名","评分","评价数","概况","相关信息","") # 列属性
    for i in range(0,8): # 写列名
        sheet.write(0,i,col[i])
    for i in range(0,250):
        print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j]) #
    book.save('豆瓣电影Top250.xls')

def saveData_db(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor() #获取游标。获取操作的数据库对象
    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            data[index] = '"'+data[index]+'"'
            # %s占位符  %",".join(data) 是将列表通过,相连接
        sql = '''
            insert into movie250 (
               info_link, pic_link,cname,ename,score,rated,introduction,info)
               values(%s) '''%",".join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

def init_db(dbpath):
    sql = '''
        create table movie250
        (
            id integer primary key autoincrement,
            info_link text,
            pic_link text,
            cname varchar,
            ename varchar,
            score numeric,
            rated numeric,
            introduction text,
            info text
        )
    '''
    conn = sqlite3.connect(dbpath) # 创建数据库
    cursor = conn.cursor() # 获取游标。获取操作的数据库对象
    cursor.execute(sql) #执行sql语句
    conn.commit() # 提交
    conn.close() #关闭数据库文件

main()
print("爬取完毕")
