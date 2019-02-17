import json
import math
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime
from datetime import timedelta

#박스오피스 순 
class BoxOffice(object):
    base_url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/'\
               'searchDailyBoxOfficeList.json'
    def __init__(self, api_key):
        self.api_key = api_key

    def get_movies(self):
        target_dt = datetime.now() - timedelta(days=1)
        target_dt_str = target_dt.strftime('%Y%m%d')
        query_url = '{}?key={}&targetDt={}'.format(self.base_url, self.api_key, target_dt_str)
        with urlopen(query_url) as fin:
            return json.loads(fin.read().decode('utf-8'))

    def simplify(self, result):
        return [
           {
              'rank': entry.get('rank'),
              'name': entry.get('movieNm'),
              'code': entry.get('movieCd')
           }
           for entry in result.get('boxOfficeResult').get('dailyBoxOfficeList')
        ]

# api_key = ''
# box = BoxOffice(api_key)
# movies = box.get_movies()
# print(box.simplify(movies))


# 상영관 정보를 가져옴
class LotteCinema(object):
    # base_url = 'http://www.lottecinema.co.kr'
    base_url = 'http://moviefriend.cafe24.com'
    base_url_cinema_data = '{}/LCWS/Cinema/CinemaData.aspx'.format(base_url)
    base_url_movie_list = '{}/LCWS/Ticketing/TicketingData.aspx'.format(base_url)

    def make_payload(self, **kwargs):
        param_list = {'channelType': 'MW', 'osType': '', 'osVersion': '', **kwargs}
        data = {'ParamList': json.dumps(param_list)}
        payload = urlencode(data).encode('utf8')
        return payload

    def byte_to_json(self, fp):
        content = fp.read().decode('utf8')
        return json.loads(content)

    def get_theater_list(self):
        url = self.base_url_cinema_data
        payload = self.make_payload(MethodName='GetCinemaItems')
        with urlopen(url, data=payload) as fin:
            json_content = self.byte_to_json(fin)
            return [
                {
                    'TheaterName': '{} 롯데시네마'.format(entry.get('CinemaNameKR')),
                    'TheaterID': '{}|{}|{}'.format(entry.get('DivisionCode'), entry.get('SortSequence'), entry.get('CinemaID')),
                    'Longitude': entry.get('Longitude'),
                    'Latitude': entry.get('Latitude')
                }
                for entry in json_content.get('Cinemas').get('Items')
            ]

    def distance(self, x1, x2, y1, y2):
        dx = float(x1) - float(x2)
        dy = float(y1) - float(y2)
        distance = math.sqrt(dx**2 + dy**2)
        return distance

    def filter_nearest_theater(self, theater_list, pos_latitude, pos_longitude, n=3):
        distance_to_theater = []
        for theater in theater_list:
            distance = self.distance(pos_latitude, theater.get('Latitude'), pos_longitude, theater.get('Longitude'))
            distance_to_theater.append((distance, theater))

        return [theater for distance, theater in sorted(distance_to_theater, key=lambda x: x[0])[:n]]

    def get_movie_list(self, theater_id):
        url = self.base_url_movie_list
        target_dt = datetime.now()
        target_dt_str = target_dt.strftime('%Y-%m-%d')
        payload = self.make_payload(MethodName='GetPlaySequence', playDate=target_dt_str, cinemaID=theater_id, representationMovieCode='')
        with urlopen(url, data=payload) as fin:
            json_content = self.byte_to_json(fin)
            movie_id_to_info = {}

            for entry in json_content.get('PlaySeqsHeader', {}).get('Items', []):
                movie_id_to_info.setdefault(entry.get('MovieCode'), {})['Name'] = entry.get('MovieNameKR')

            for order, entry in enumerate(json_content.get('PlaySeqs').get('Items')):
                schedules = movie_id_to_info[entry.get('MovieCode')].setdefault('Schedules', [])
                schedule = {
                    'StartTime': '{}'.format(entry.get('StartTime')),
                    'RemainingSeat': int(entry.get('TotalSeatCount')) - int(entry.get('BookingSeatCount'))
                }
                schedules.append(schedule)
            return movie_id_to_info

# cinema = LotteCinema()

# print(cinema.filter_nearest_theater(cinema.get_theater_list(), 37.5, 126.844))
# print(cinema.get_movie_list('1|2|1018'))
