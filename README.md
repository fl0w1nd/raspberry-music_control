# 树莓派基于python的Flask web音乐播放器 #

### 界面 ###

![](https://raw.githubusercontent.com/fl0w1nd/img/master/image/music_control.png)

### 功能 ###

* 上一首
* 下一首
* 播放/暂停
* 列表切换音乐
* 音量控制条

## 依赖 ##

### cmus ###
**cmus** is a fast and light music player for Unix-like operating systems. It's intended to be used mostly by the console, but it also opens a TCP port in the system which creates a new way to interact with it for the use.

### Flask ###
**Flask** is a Python framework oriented to create and handle a server. It's supposed to be simple and easily usable.

### PyCmus ###
Small library for Python with methods for connecting to a **cmus** by sockets. Its [repo](https://github.com/mtreinish/pycmus).

### TinyTag ###
Extracts information from an audio file and stores it in an object whose attributes are the file's ones. [Repository](https://github.com/mtreinish/pycmus).

## 使用 ##

### 安装cmus ###

```console
user@system:~$ sudo apt install cmus 
```
### python安装Flask ###

```console
user@system:~/raspberry-music_control$ python3 -m venv venv
user@system:~/raspberry-music_control$ source venv/bin/activate
(venv) user@system:~/raspberry-music_control$ pip install Flask
```

### 运行 ###
```console
user@system:~/raspberry-music_control$ python3 run_webapp.py
```

默认端口号:5000
