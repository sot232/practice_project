# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_client.bot import BaseBot
from bothub_client.decorators import channel
from bothub_client.decorators import command
from bothub_client.messages import Message
from .movies import BoxOffice
from .movies import LotteCinema

class Bot(BaseBot):
    def handle_message(self, event, context):
        message = event.get('content')
        location = event.get('location')

        if location:
            self.send_nearest_theaters(location['latitude'], location['longitude'])
            return

        if message == '영화순위':
            self.send_box_office(event)
        elif message == '근처 상영관 찾기':
            self.send_search_theater_message(event)
        elif message.startswith('/schedule'):
            _, theater_id, theater_name = message.split(maxsplit=2)
            self.send_theater_schedule(theater_id, theater_name, event)
        elif message == '/start':
            self.send_welcome_message(event)
        else:
            self.send_error_message(event)

    def send_error_message(self, event):
        message = Message(event).set_text('잘 모르겠네요.\n\n'\
                                          '저는 요즘 볼만한 영화들을 알려드리고, '\
                                          '현재 계신 곳에서 가까운 영화관들의 상영시간표를 알려드려요.\n\n'
                                          "'영화순위'나 '근처 상영관 찾기'를 입력해보세요.")\
                                .add_quick_reply('영화순위')\
                                .add_quick_reply('근처 상영관 찾기')
        self.send_message(message)

    @command('start')
    def send_welcome_message(self, event):
        message = Message(event).set_text('반가워요.\n\n'\
                                          '저는 요즘 볼만한 영화들을 알려드리고, '\
                                          '현재 계신 곳에서 가까운 영화관들의 상영시간표를 알려드려요.\n\n'
                                          "'영화순위'나 '근처 상영관 찾기'를 입력해보세요.")\
                                .add_quick_reply('영화순위')\
                                .add_quick_reply('근처 상영관 찾기')
        self.send_message(message)

    @command('schedule')
    def send_theater_schedule(self, theater_id, theater_name, event):
        c = LotteCinema()
        movie_id_to_info = c.get_movie_list(theater_id)

        text = '{}의 상영시간표입니다.\n\n'.format(theater_name)

        movie_schedules = []
        for info in movie_id_to_info.values():
            movie_schedules.append('* {}\n  {}'.format(info['Name'], ' '.join([schedule['StartTime'] for schedule in info['Schedules']])))

        message = Message(event).set_text(text + '\n'.join(movie_schedules))\
                                .add_quick_reply('영화순위')\
                                .add_quick_reply('근처 상영관 찾기')
        self.send_message(message)

    def send_nearest_theaters(self, latitude, longitude, event):
        c = LotteCinema()
        theaters = c.get_theater_list()
        nearest_theaters = c.filter_nearest_theater(theaters, latitude, longitude)

        message = Message(event).set_text('가장 가까운 상영관들입니다.\n' + \
                                          '상영 시간표를 확인하세요:')

        for theater in nearest_theaters:
            data = '/schedule {} {}'.format(theater['TheaterID'], theater['TheaterName'])
            message.add_postback_button(theater['TheaterName'], data)

        message.add_quick_reply('영화순위')
        self.send_message(message)


    def send_search_theater_message(self, event):
        message = Message(event).set_text('현재 계신 위치를 알려주세요(This feature will not work if you do not live in Korea.)')\
                                .add_location_request('위치 전송하기')
        self.send_message(message)

    @command('boxoffice')
    def send_box_office(self, event):
        data = self.get_project_data()
        # api_key = data.get('box_office_api_key')
        api_key = '' # you should get your own api key.
        box_office = BoxOffice(api_key)
        movies = box_office.simplify(box_office.get_movies())
        rank_message = ', '.join(['{}. {}'.format(m['rank'], m['name']) for m in movies])
        response = '요즘 볼만한 영화들의 순위입니다\n{}'.format(rank_message)

        message = Message(event).set_text(response)\
                                .add_quick_reply('영화순위')\
                                .add_quick_reply('근처 상영관 찾기')
        self.send_message(message)
