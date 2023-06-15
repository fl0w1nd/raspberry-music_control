try:
    from flask import Flask, render_template, request, jsonify
except (ModuleNotFoundError, ImportError):
    from pip import main
    main(['install', 'flask'])
import json

class MusicControllerWeb(object):
    """
    此类处理用于我们应用程序的 Web

    :param str name: 应用程序的名称
    :param PyCmus cmus: cmus 处理程序
    """
    def __init__(self, name, cmus, songs):
        """
        类的构造函数。它初始化 Flask 对象并渲染 Web
        """
        super(MusicControllerWeb, self).__init__()
        # Flask 的主要方法
        self.app = Flask(
            name, template_folder="webserver/templates", static_folder="webserver/static"
        )
        # cmus 控制器
        self.cmus = cmus
        # 歌曲信息
        self.songs_info = MusicControllerWeb.songs_info_extraction(songs)
        # 歌曲状态。存储本地信息
        self.status = {
            'current_song': 0,
            'playing': False,
            'volume': 30
        }
        # 渲染Web
        self._render_web()

    def _render_web(self):
        """
        渲染 Web 将使用的域名
        """

        @self.app.route('/')
        def index():
            return render_template(
                'mainpage.html', 
                is_playing=self.status['playing'], 
                songs = self.songs_info['songs'],
                num_songs = self.songs_info['num_songs'],
                first_song = self.status['current_song'],
                volume=self.status['volume']  # 将音量值传递
            )


        @self.app.route('/set_volume', methods=['POST'])
        def set_volume():
            data = request.get_json()
            volume = int(data['volume'])
            self.status['volume'] = volume
            self.cmus.set_volume(volume)
            return '', 200


        @self.app.route('/_post_data', methods = ['POST'])
        def worker():
            jsonData = request.get_json()
            self._post_handler(jsonData)
            return jsonify(
                success=True,
                data=(self.status,self.songs_info['songs'])
            )


    def _post_handler(self, jsonData):
        """
        使用服务器从客户端接收的数据，
        并将其转化为对 cmus 的命令

        :param lst jsonData: 包含数据的字典
        """

        # Web 应用程序上实现的按钮
        buttons = {
            1: 'player',
            2: 'prev',
            3: 'next',
            4: 'new_song'
            
        }

        btn_clicked = jsonData['button']
        try:
            if btn_clicked == buttons[1]:
                # 播放按钮
                if self.status['playing'] is True:
                    self.cmus.player_pause()
                else:
                    self.cmus.player_play_file(
                        self.cmus.player_play()
                    )
                self.status['playing'] = not(self.status['playing'])
            elif btn_clicked == buttons[2]:
                # 下一首按钮
                if self.status['current_song'] > 0:
                    self.status['current_song'] -= 1
                self.start_playing_current_song()
                self.status['playing'] = True
            elif btn_clicked == buttons[3]:
                # 上一首按钮
                if self.status['current_song'] < self.songs_info['num_songs']-1:
                    self.status['current_song'] += 1
                self.start_playing_current_song()
                self.status['playing'] = True
            elif btn_clicked == buttons[4]:
                new_song = int(jsonData["song"])
                if (new_song >= 0) and (new_song < self.songs_info['num_songs']):
                    self.status['current_song'] = new_song
                    self.start_playing_current_song()
                    self.status['playing'] = True
                else:
                    print("Selected song #{} is unrecheable".format(new_song))
            else:
                pass
        except BrokenPipeError as err:
            MusicControllerWeb._cmus_connection_failed(err)


    @staticmethod
    def songs_info_extraction(raw_songs):
        """
        我们只需要来自包含歌曲数据的变量的一些信息。
        然后，此方法提取此信息。
        此外，为了在服务器和客户端之间共享信息，
        必须将其转换为字典或类似的形式，
        因为 Tinytag 对象无法序列化，因此无法发送
        
        :param obj: MusicExtractor 对象。它包含所有的音乐信息
        :return songs_info: 封面图像文件夹路径、歌曲数量和相关信息
        :rtype: dict
        """
        songs = list(
            {'filename': song[0],'title':song[1].title, 'artist': song[1].artist} 
            for song in raw_songs.songs_list
        )
        return ({
            'covers_folder': raw_songs.covers_folder,
            'num_songs': raw_songs.num_songs,
            'songs': songs
        })

    
    def start_playing_current_song(self):
        self.cmus.player_play_file(
            self.songs_info['songs'][self.status['current_song']]['filename']
        )


    @staticmethod
    def _cmus_connection_failed(err):
        """
        如果与 cmus 的连接中断，我们调用此方法
        """
        print('Connection with cmus has been closed: {}'.format(err))
        try:
            print('Closing server',end='')
            MusicControllerWeb.shutdown_server()
            print('ok')
        except Exception as err2:
            from sys import exit
            print('\nSome problem occured: {}'.format(err2))
            exit('Exiting program...')


    @staticmethod
    def shutdown_server():
        """
        关闭我们用 Flask 打开的 werkzeug 服务器。
        当与 cmus 的连接断开时使用
        """
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()