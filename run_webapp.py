#!./venv/bin/python3

from pycmus import remote, exceptions

import sys
import os
import time


def exit_cmus(cmus, cmus_process):
    """
    关闭在程序启动时打开的 cmus 进程
    """
    try:
        cmus.send_cmd('quit\n')
    except BrokenPipeError:
        pass
    finally:
        try:
            cmus_process.terminate()
        except OSError:
            try:
                cmus_process.kill()
            except OSError:
                pass

def init_cmus(cmus, music_folder, first_song):
    """
    停止播放器（如果正在播放歌曲），
    清除环境（实际上并不必要），
    并添加我们选择的文件夹中的音乐
    """
    cmus.send_cmd('player-stop\n')
    cmus.send_cmd('clear\n')
    cmus.send_cmd('add {}\n'.format(music_folder))
    # 选择要播放的歌曲
    cmus.player_play_file(first_song)
    cmus.player_stop()

def main(port=5000, music_folder='music/'):
    """
    主函数。
    :param int port: 服务器将在其中运行的端口
    :param str music_folder: 音乐所在的目录
    """
    # 创建一个新进程，在其中执行 cmus
    try:
        import subprocess
        cmus_process = subprocess.Popen(args=["cmus"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as err:
        print('Impossible to open a new cmus instance: {}'.format(err))
    finally:
        # 尝试连接到 cmus 服务
        max_time = 5
        start_time = time.time()
        while True:
            try:
                print('Trying to connect to cmus... ', end='')
                cmus = remote.PyCmus()
                break
            except exceptions.CmusNotRunning:
                if (time.time() - start_time <= max_time):
                    #如果连接被拒绝，但尚未超过最大时间，则再次尝试
                    time.sleep(1)
                    continue 
                else:
                    print('\nImpossible to connect to cmus. Exiting the program...')
                    try:
                        exit_cmus(cmus, cmus_process)
                    except UnboundLocalError:
                        pass
                    finally:                        
                        sys.exit(1)
        print('ok\n')

        # 获取将要播放的歌曲
        import music_extractor
        songs = music_extractor.MusicExtractor(music_folder)
        if not(songs.num_songs):
            print("There aren't any songs in the chosen directory. Exiting program... ")
            exit_cmus(cmus, cmus_process)
            sys.exit(1)
        # '重启' cmus
        init_cmus(cmus, songs.music_folder, songs.songs_list[0][0])
        # 打开 web 服务器
        try:
            from webserver.webapp import MusicControllerWeb
            flask_object = MusicControllerWeb(__name__, cmus, songs)
            flask_object.app.run(
                debug=False,
                host='0.0.0.0',
                threaded=True,
                port=port
            )
        except Exception as err:
            print('Some problem occured: ', end='')
            print(err)
            sys.exit('Exiting program...')
        # 删除包含歌曲封面的目录
        songs.del_covers_folder()
        # 在离开程序之前，关闭与 cmus 的连接
        exit_cmus(cmus, cmus_process)

if __name__ == '__main__':
    # 可以从终端选择端口和音乐文件夹
    # 用于我们将使用的应用程序
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', action="store", dest="port", default=5000, type=int,
        help='Select the port it will be used for the server'
    )
    parser.add_argument(
        '-mf', action="store", dest="music_folder", default='music/', type=str,
        help='Select the path for the folder'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    input_val = parser.parse_args()
    main(input_val.port, input_val.music_folder)
    