import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import datetime
import json

class data_model:
    def __init__(self):
        pass

    def movie_suggest(self, rating_data):
        '''
        피어슨 상관계수를 이용한 영화 추천 알고리즘
        :param rating_data:
        :return:
        '''

        '''
        # 피어슨 상관계수 계산
        pd.options.display.max_rows = 100

        file = pd.read_csv('../data/ratings.csv')
        df = pd.DataFrame(file)

        test = df.groupby(['movieId'])[['rating']].count()
        test = test.sort_values(by='rating', ascending=False)
        
        most_rated_movies = test[test['rating'] >= 10000]
        
        data = df[df['movieId'].isin(most_rated_movies.index)]
        
        user_ratings = data.pivot_table(index=['userId'], columns=['movieId'], values=['rating'])
        
        user_ratings = user_ratings.dropna(thresh=10, axis=1).fillna(0)
        
        item_similarity_df = user_ratings.corr(method='pearson')
       
        new_idx = item_similarity_df.reset_index()['movieId']

        print(item_similarity_df.set_index(new_idx).T.set_index(new_idx).T)

        item_similarity_df = item_similarity_df.set_index(new_idx).T.set_index(new_idx).T

        item_similarity_df.to_csv('./item_similarity_df.csv', index=True)
        '''


        item_similarity_df = pd.DataFrame()
        item_similarity_df = pd.read_csv('./data/item_similarity_df.csv')

        new_idx = item_similarity_df.reset_index()['movieId']

        item_similarity_df = item_similarity_df.set_index(new_idx)
        item_similarity_df = item_similarity_df.drop(columns='movieId')

        # 가중치 및 음의 관계, 양의 관계 변환
        def get_similar_movies(movie_id, user_rating):
            similar_score = item_similarity_df.loc[:, movie_id] * (float(user_rating) - 2.49)
            similar_score = similar_score.sort_values(ascending=False)
            return similar_score

        similar_movies = pd.DataFrame()

        for movie, rating in rating_data:
            similar_movies = similar_movies.append(get_similar_movies(movie, rating))

        # 추천 리스트 중 6개 출력
        return similar_movies.sum().sort_values(ascending=False).head(6).index


    def sim_movie(self, title):
        '''
        surprise 라이브러리(코사인 유사도)를 이용한 영화 추천
        :param title:
        :return:
        '''
        import sys, gc

        # Load movies data
        movies = pd.read_csv('./data/movies.csv')
        genome_scores = pd.read_csv('./data/genome-scores.csv')
        tags = pd.read_csv('./data/tags.csv')
        genome_tags = pd.read_csv('./data/genome-tags.csv')
        # Use ratings data to downsample tags data to only movies with ratings
        ratings = pd.read_csv('./data/ratings.csv')
        # ratings = ratings.drop_duplicates('movieId')

        ratings_f = ratings.groupby('userId').filter(lambda x: len(x) >= 1000)
        movie_list_rating = ratings_f.movieId.unique().tolist()
        movies = movies[movies.movieId.isin(movie_list_rating)]
        # map movie to id:
        Mapping_file = dict(zip(movies.title.tolist(), movies.movieId.tolist()))
        tags.drop(['timestamp'], 1, inplace=True)
        ratings_f.drop(['timestamp'], 1, inplace=True)

        mixed = pd.DataFrame()
        Final = pd.DataFrame()
        mixed = pd.merge(movies, tags, on='movieId', how='left')

        mixed.fillna("", inplace=True)
        mixed = pd.DataFrame(mixed.groupby('movieId')['tag'].apply(lambda x: "%s" % ' '.join(x)))
        Final = pd.merge(movies, mixed, on='movieId', how='left')
        Final['metadata'] = Final[['tag', 'genres']].apply(lambda x: ' '.join(x), axis=1)
        Final[['movieId', 'title', 'metadata']].head(3)



        from sklearn.feature_extraction.text import TfidfVectorizer
        # Creating a content latent matrix from movie metadata:
        # tf-idf vectors and truncated SVD:

        tfidf = TfidfVectorizer(stop_words='english')

        tfidf_matrix = tfidf.fit_transform(Final['metadata'])


        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), index=Final.index.tolist())


        # The first 200 components explain over 50% of the variance:
        # Compress with SVD
        from sklearn.decomposition import TruncatedSVD
        svd = TruncatedSVD(n_components=200)
        latent_matrix = svd.fit_transform(tfidf_df)

        # number of latent dimensions to keep
        n = 200
        latent_matrix_1_df = pd.DataFrame(latent_matrix[:, 0:n], index=Final.title.tolist())

        # our content latent matrix:
        latent_matrix.shape  # (26694,200)

        # creating a collaborative latent matrix from user ratings:
        ratings_f1 = pd.merge(movies[['movieId']], ratings_f, on="movieId", how="right")



        ratings_f2 = ratings_f1.pivot(index='movieId', columns='userId', values='rating').fillna(0)

        from sklearn.decomposition import TruncatedSVD
        svd = TruncatedSVD(n_components=200)
        latent_matrix_2 = svd.fit_transform(ratings_f2)
        latent_matrix_2_df = pd.DataFrame(
            latent_matrix_2,
            index=Final.title.tolist())



        from sklearn.metrics.pairwise import cosine_similarity
        # take the latent vectors for a selected movie from both content
        # and collaborative matrices

        a_1 = np.array(latent_matrix_1_df.loc[title]).reshape(1, -1)
        a_2 = np.array(latent_matrix_2_df.loc[title]).reshape(1, -1)

        # calculate the similarity of this movie with the others in the list
        score_1 = cosine_similarity(latent_matrix_1_df, a_1).reshape(-1)
        score_2 = cosine_similarity(latent_matrix_2_df, a_2).reshape(-1)

        # an average measure of both content and collaborative
        hybrid = ((score_1 + score_2) / 2.0)

        # form a data frame of similar movies
        dictDf = {'content': score_1, 'collaborative': score_2, 'hybrid': hybrid}
        similar = pd.DataFrame(dictDf, index=latent_matrix_1_df.index)

        # sort it on the basis of either: content, collaborative or hybrid,
        # here : content
        similar.sort_values('content', ascending=False, inplace=True)
        return similar[0:].head(11).index


    def datashow(self, movieId):
        '''
        영화별, 장르별 시간에 따른 평점 추이
        :param movieId:
        :return:
        '''

        '''
        print("timestamp 변환")
        file = pd.read_csv('../data/ratings.csv')
        frame = pd.DataFrame(file)
        
        date_data = []
        time_data = []
        hour_data = []
        obj = frame.loc[0:, "timestamp"]
        
        for i in obj:
            # print(i)
            timetodate = datetime.datetime.fromtimestamp(i / 1000)
            # 연 월 일
            date_data.append(timetodate.strftime("%Y%m%d"))
            # 시간 분
            time_data.append(timetodate.strftime("%H%M"))
            #  시간
            hour_data.append(timetodate.strftime("%H"))
            
        date_series = pd.Series(date_data)
        time_series = pd.Series(time_data)
        hour_series = pd.Series(hour_data)
        
        frame['date_series'] = date_series
        frame['time_series'] = time_series
        frame['hour_series'] = hour_series
        frame.to_csv("../data/movie_genres.csv", index=False)
        '''


        file = pd.read_csv('./data/movie_genres.csv')
        frame = pd.DataFrame(file)

        frame = frame[(frame['movieId'] == int(movieId))]

        frame.to_csv("../data/obj1.csv", index=False)

        hour_avg = frame.groupby(frame['hour_series'])[['rating']].mean()
        hour_count = frame.groupby(frame['hour_series'])[['rating']].count()

        user_avg = frame.groupby(['userId', 'hour_series'])[['rating']].mean()

        hour_avg.to_csv("../data/hour_temp.csv")
        hour_avg = pd.read_csv("../data/hour_temp.csv")

        hour_count.to_csv("../data/hour_count.csv")
        hour_count = pd.read_csv("../data/hour_count.csv")

        user_avg.to_csv("../data/user_avg.csv")
        user_avg = pd.read_csv("../data/user_avg.csv")
        user_avg = user_avg[(user_avg['userId'] == 1)]


        return json.loads(hour_avg.to_json())
