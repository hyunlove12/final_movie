from bs4 import BeautifulSoup
from urllib.request import urlopen as uo
import urllib.request
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import math
from dataanaly.dh.model import SamsungReport as sr
import nltk

def __init__(self, item):
    self.item = item
    self.url = 'https://finance.naver.com/item/sise_day.nhn?code={item}'.format(item=self.item)
    self.df = pd.DataFrame()


def scrap(self):
    url = 'https://finance.naver.com/item/sise_day.nhn?code={item}'.format(item=self.item)
    uo(url)
    #class = tah p11
    soup = BeautifulSoup(uo(url), "html.parser")
    for i in soup.find_all(name="span", attrs=({"class":"tah"})):
        print(str(i.text))


#페이징 처리된 부분의 주식정보 가져오기
def selWeb():
    driver = webdriver.Chrome(executable_path='D:/chromedriver')
    driver.implicitly_wait(3)
    driver.get('https://movie.naver.com/movie/bi/mi/point.nhn?code=36732')

    #self.driver.find_element_by_name('id').send_keys('')
    #self.driver.find_element_by_name('pw').send_keys('')
    driver.implicitly_wait(3)
    # 정규식
    # *// 어떠한 값이 오는 경우에도
    # id의 속성이 []안에 있는 값일 경우
    # click 이벤트 전달
    #self.driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

    # self.driver.find_element_by_xpath('//tbody/tr/td[@class="pgR"]/a').click()
    # self.driver.implicitly_wait(3)

 #   self.driver.get('https://order.pay.naver.com/home')
    #화면에 있는 그대로의 html
    # driver.find_element_by_xpath('//iframe[@id="pointAfterListIframe"]').

    # iframes = driver.find_elements_by_css_selector('iframe')
    # for iframe in iframes:
        # print(iframe.get_attribute('name'))

    driver.switch_to.frame(driver.find_element_by_id("pointAfterListIframe"))
    # driver.switch_to.default_content()


    total_review_count = driver.find_element_by_css_selector('strong.total > em').text
    print(total_review_count)
    # 이것으로 sleep을 주면 dom이 렌더링 되는 속도보다 parsing되는 속도가 빨라 최신 페이지 반영이 안되는 경우가 있따.
    # driver.implicitly_wait(100000000)



    # element = WebDriverWait(driver, 10).until(
        # EC.element_to_be_clickable((By.XPATH, '//a[@id="pagerTagAnchor' + '2' + '"]'))
    # )
    # element.click()

    # html = driver.page_source
    # soup = BeautifulSoup(html, 'html.parser')
    # select와 find의 차이
    # score_result = soup.select('div.score_result > ul > li')

    # total_review_count = soup.select_one('strong.total > em').text
    print('총 리뷰건수 : ',  total_review_count)

    paging = int(total_review_count.replace(',','')) / 10
    print("총 페이징 수 : ", paging)

    # 평점 시리즈
    review_series = []
    # 글쓴이 시리즈
    writer_series = []
    # 연월일시간 시리즈
    ymdt_series = []
    # 날짜 시리즈
    date_series = []
    # 시분 시리즈
    time_series = []
    # 시간 시리즈
    hour_series = []

    f = open('test.txt', mode='wt', encoding='utf-8')
    for e in range(math.ceil(round(200))):
        driver.find_element_by_xpath('//a[@id="pagerTagAnchor' + str(e + 1) + '"]').click()
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # select와 find의 차이
        score_result = soup.select('div.score_result > ul > li')

        review = ''
        for i in score_result:
            print("++++++++++++++++++++++++++++++++++++++++++++")
            # 평점
            print(i.select_one('div.star_score > em').text)
            review_series.append(i.select_one('div.star_score > em').text)
            # 리뷰
            if i.select_one('span[id*="_unfold_ment"] > a') is None:
                review = i.select_one('span[id*="_filtered_ment"]').text.strip()
                print(i.select_one('span[id*="_filtered_ment"]').text.strip())
            else:
                review = i.select_one('span[id*="_unfold_ment"] > a').get('data-src').strip()
                print(i.select_one('span[id*="_unfold_ment"] > a').get('data-src').strip())
            # 글쓴이
            print(i.select_one('dl > dt > em:nth-of-type(1) > a > span').text)
            writer_series.append(i.select_one('dl > dt > em:nth-of-type(1) > a > span').text)
            # 리뷰날짜
            print(i.select_one('dl > dt > em:nth-of-type(2)').text)
            ymdt_series.append(i.select_one('dl > dt > em:nth-of-type(2)').text)
            # 연월일
            print(i.select_one('dl > dt > em:nth-of-type(2)').text.split(' ')[0].replace('.', ''))
            date_series.append(i.select_one('dl > dt > em:nth-of-type(2)').text.split(' ')[0].replace('.', ''))
            # 시간
            print(i.select_one('dl > dt > em:nth-of-type(2)').text.split(' ')[1].replace(':', ''))
            time_series.append(i.select_one('dl > dt > em:nth-of-type(2)').text.split(' ')[1].replace(':', ''))
            print(i.select_one('dl > dt > em:nth-of-type(2)').text.split(' ')[1].replace(':', '')[0:2])
            hour_series.append(i.select_one('dl > dt > em:nth-of-type(2)').text.split(' ')[1].replace(':', '')[0:2])
            print("==========================================")
            f.writelines(review + '\n')
    f.close()

    # 평점 시리즈
    # review_series = pd.Series()
    # 글쓴이 시리즈
    # writer_series = pd.Series()
    # 연월일시간 시리즈
    # ymdt_series = pd.Series()
    # 날짜 시리즈
    # date_series = pd.Series()
    # 시간 시리즈
    # time_series = pd.Series()

    data = {
            'review' : review_series
           ,'writer' : writer_series
           , 'ymdt': ymdt_series
           , 'date': date_series
           , 'time': time_series
           , 'hour': hour_series
           }

    frame = pd.DataFrame(data)

    print(frame)
    frame.to_csv("./movie_rating.csv", index=False, encoding='utf-8')
    #컬럼 명
    # stock_columns = ['날짜', '종가', '전일비', '시가', '고가', '저가', '거래량']

    # temp = []
    # num = 1
    # result = soup.find("")
    #tr단위로 저장
    # for b in tr:
        #print(b)
        #print(b.text)
        # for i in b.find_all(name="span", attrs=({"class":"tah"})):
            #print(str(i))
            #print(str(i.text))
            #strip() -> \n \t 등 각종 개행문자 제거
            # temp.append(str(i.text).strip())
            # print("=========")
            #print(temp)
        # print("td값 종료")
        # if len(temp) > 0:
            #data = {temp[0]:temp[1:]}
            #self.df[temp[0]] = temp[1:]
            #self.df = temp[:]

            #행 추가
            #self.df.loc[num] = temp[:]

            #열 추가
            # df[num] = temp[:]
            # num = num + 1
       # temp = []
    #행과 열 전치 -> transpose() or T
    #self.df.columns = stock_columns
    #컬럼 추가는 데이터프레임이 널이 아니여야 가능
    # print(df)
    # df = df.transpose()
    # df.columns = stock_columns
    #컬럼명 추가
    #self.df.columns = stock_columns
    # print(df)
    #csv로 저장
    # df.to_csv('D:\Output.csv', encoding='utf-8-sig')
    #for i in notices:
    #    print(i.text.strip())

def image_():
    movie_list = pd.read_csv('./movie_list.csv')
    # print(movie_list)
    print("+++++")
    index_series = movie_list['title']
    title_series = movie_list['genres']
    print(index_series)

    driver = webdriver.Chrome(executable_path='D:/chromedriver')
    driver.implicitly_wait(3)
    driver.get('https://movie.naver.com/')

    for i, e in enumerate(index_series):
        driver.find_element_by_id('ipt_tx_srch').send_keys(e)
        # self.driver.find_element_by_name('pw').send_keys('')
        driver.implicitly_wait(3)
        # 정규식
        # *// 어떠한 값이 오는 경우에도
        # id의 속성이 []안에 있는 값일 경우
        # click 이벤트 전달
        driver.find_element_by_xpath('//*[@class="btn_srch"]').click()



        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        score_result = ''
        # select와 find의 차이
        if soup.select_one('ul.search_list_1 > li > p > a > img') is not None:
            score_result = soup.select_one('ul.search_list_1 > li > p > a > img').get('src')
            print(score_result)
            urllib.request.urlretrieve(score_result, './img/' + title_series[i])





        # 평점 시리즈
        review_series = []
        # 글쓴이 시리즈
        writer_series = []
        # 연월일시간 시리즈
        ymdt_series = []
        # 날짜 시리즈
        date_series = []
        # 시분 시리즈
        time_series = []
        # 시간 시리즈
        hour_series = []


def movie_info():
    movie_list = pd.read_csv('./movie_list.csv')
    # print(movie_list)
    print("+++++")
    index_series = movie_list['title']
    title_series = movie_list['genres']
    print(index_series)

    driver = webdriver.Chrome(executable_path='D:/chromedriver')
    driver.implicitly_wait(3)
    driver.get('https://movie.naver.com/')

    for i, e in enumerate(index_series):
        driver.find_element_by_id('ipt_tx_srch').send_keys(e)
        # self.driver.find_element_by_name('pw').send_keys('')
        driver.implicitly_wait(3)
        # 정규식
        # *// 어떠한 값이 오는 경우에도
        # id의 속성이 []안에 있는 값일 경우
        # click 이벤트 전달
        driver.find_element_by_xpath('//*[@class="btn_srch"]').click()
        driver.find_element_by_xpath('//*[@class="result_thumb"]/a').click()
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        print(soup.select_one('div#content > div > div > div > div > h3 > a'))


if __name__ == "__main__":
    print("시작")
    # selWeb()
    # s = sr()
    # nltk.download()
    # s.find_freq()
    # s.draw_wordcloud()
    # image_()
    movie_info()