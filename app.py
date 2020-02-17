from flask import Flask
from flask import render_template, request, jsonify
import re
import db_connection as db_conn
from model import data_model as dm


app = Flask(__name__)

'''
# 기본 데이터 set -> movielens
# item_similarity_df.csv -> 피어슨 상관계수 데이터set
# movie_list.csv -> 피어슨 상관계수에 들어있는 영화 목록
# movie_genres.csv -> 시간별, 날짜별 데이터 분류를 진행한 목록 -> 용량으로 인한 업로드 제한
# 그 외 데이터(영화정보, 리뷰데이터, 이미지 등) -> 네이버 영화 크롤링
# 알고리즘 호출하는 로직 개선 필요 -> 속도
'''

@app.route('/main', methods=['post'])
def main():
    '''
    선택된 6개 영화에 대한 추천 영화 리스트 출력
    :return:
    '''
    movielist = request.form.getlist('movieid')
    ratinglist = request.form.getlist('movierating')

    data_model = dm()
    movie_tuple = []
    for i, e in enumerate(movielist):
        movie_tuple.append((e, ratinglist[i]))
    print(movie_tuple)
    movie_list = data_model.movie_suggest(movie_tuple)
    print(list(movie_list))
    conn = db_conn.conn()
    curs = conn.cursor()
    sql = "SELECT * FROM MOVIE_LIST WHERE MOVIE_ID IN (%s,%s,%s,%s,%s,%s)"
    curs.execute(sql, (str(movie_list[0]),str(movie_list[1]), str(movie_list[2]), str(movie_list[3]), str(movie_list[4]), str(movie_list[5])))
    rows = curs.fetchall()
    sql_lists = list()
    for i,e,a in rows:
        sql_lists.append({
                           'movie_id':i
                         , "title":e
                         , "img_title":a
                        })

    print(sql_lists)
    conn.close()
    return render_template('index.html', sql_list=sql_lists)

@app.route('/')
def index():
    '''
    메인페이지 - 랜덤 6개 영화에 대한 평점 주는 페이지
    평점 후 메인페이지로 전환
    :return:
    '''
    conn = db_conn.conn()
    curs = conn.cursor()
    sql = "SELECT * FROM MOVIE_LIST ORDER BY RAND() LIMIT 6"
    curs.execute(sql)
    rows = curs.fetchall()
    sql_lists = list()
    for i,e,a in rows:
        sql_lists.append({
                           'movie_id':i
                         , "title":e
                         , "img_title":a
                        })

    print(sql_lists)
    conn.close()
    return render_template('work.html', sql_list=sql_lists)

@app.route('/detail/<movie_id>')
def detail(movie_id):
    '''
    선택 한 영화에 대한 상세정보
    영화정보 및 영화에 대한 데이터 분석 정보
    :param movie_id:
    :return:
    '''
    conn = db_conn.conn()
    curs = conn.cursor()
    sql = "SELECT * FROM MOVIE_LIST WHERE MOVIE_ID = %s"
    curs.execute(sql, movie_id)
    rows = curs.fetchall()
    sql_lists = list()
    for i,e,a in rows:
          dict_result = {
                           'movie_id':i
                         , "title":e
                         , "img_title":a
                        }
    conn.close()
    '''
    # json형태로 데이터 넘겨서 구글chart로 표시
    # json형태 변환에서 오류
    # 주석처리
    # data_model = dm()
    # hour_avg = data_model.datashow(movie_id)

    # print(dict(json.dumps(hour_avg['rating'],ensure_ascii=False)))

    # json_hour = json.dumps(hour_avg['rating'],ensure_ascii=False)
    # json_hour = jsonify(dict(hour_avg['rating']))
    #    dict(json_hour)
    # print(json_hour)
    # json_hour = hour_avg.to_json()
    '''
    return render_template('detail.html', dict_results=dict_result, title=dict_result['title'])


@app.route('/search', methods=['post'])
def search():
    '''
    검색 한 영화에 대한 surprise알고리즘에 대한 추천 영화 리스트 출력
    :param movie_id:
    :return:
    '''
    movie_title = request.form['movie_title']
    conn = db_conn.conn()
    curs = conn.cursor()

    like_cur = "%" + movie_title + "%"

    sql = """SELECT * FROM MOVIE_LIST WHERE TITLE LIKE %s"""
    curs.execute(sql, (like_cur))
    title_ = curs.fetchone()[1]

    data_model = dm()
    sug_list = data_model.sim_movie(title_)

    conn.close()

    sql = """SELECT * FROM MOVIE_LIST WHERE TITLE IN ("""
    a = ''
    list_tuple = []
    for i, e in enumerate(sug_list):
        list_tuple.append(sug_list[i].strip())
        if(i == (sug_list.size - 1) ):
            a += '%s )'
        else:
            a += '%s ,'
    sql += a
    conn = db_conn.conn()
    curs = conn.cursor()
    curs.execute(sql, tuple(list_tuple))
    rows = curs.fetchall()
    sql_lists = list()
    for i,e,a in rows:
        sql_lists.append({
                           'movie_id':i
                         , "title":e
                         , "img_title":a
                        })
    conn.close()
    return render_template('index.html', sql_list=sql_lists, type="search", result=len(rows))


@app.route('/searchajax/<movie_id>', methods=['POST'])
def searchajax(movie_id):
    '''
    검색 컨트롤러 - ajax 사용안함
    :param movie_id:
    :return:
    '''
    conn = db_conn.conn()
    curs = conn.cursor()
    sql = "SELECT MOVIE_ID, TITLE, IMG_TITLE FROM MOVIE_LIST WHERE MOVIE_ID = %s"
    curs.execute(sql, (movie_id))
    # fetachall을 사용하면 curs에 있는 값이 모두 날라간다.
    rows = curs.fetchall()
    if len(rows) > 0:
        print("검색 결과 존재")
    else:
        print("검색 결과 없음")
        return "검색 결과가 없습니다."
    conn.close()
    return "{}건의 검색결과가 있습니다.".format(len(rows))


if __name__ == "__main__":
#    app.run(host="0.0.0.0")
    app.run()