import sys
import threading
import webbrowser
import excformat
import winsound
from winsound import SND_ASYNC
import uuid
from pywinstyles import apply_style
from hddLoading import QtCore, Ui_Form
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QGraphicsOpacityEffect
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import Qt ,QEventLoop , QTimer , QPropertyAnimation
from PyQt5.QtGui import QFontDatabase , QPainter , QPixmap , QFont , QTextCursor , QIcon
from PyQt5 import QtGui
from Icon import Ui_Icon
from MainPage import Ui_MainPage
from errorScreen import Ui_error
from loadingScreen import Ui_loading
from aboutScreen import Ui_about
from exitScreen import Ui_exit
import ctypes
import requests
import pygame
import systemInfo

def scroll_text_in_label(win, label: QTextEdit, text_lines: str, interval_ms: int = 1000):
    current_line = 0
    text_lines = text_lines.split("\n")

    # 创建定时器  
    timer = QTimer(win)

    # 定时器超时时的回调函数  
    loop = QEventLoop(win)

    def on_timeout():
        nonlocal current_line  # 声明current_line为nonlocal，以便在内部函数中修改  
        if current_line < len(text_lines):
            # 追加文本并换行  
            label.setText(label.toPlainText() + text_lines[current_line] + "\n")
            current_line += 1
        else:
            # 所有文本都已显示，停止定时器  
            timer.stop()
            loop.quit()

    # 连接定时器超时信号到回调函数  
    timer.timeout.connect(on_timeout)

    # 启动定时器  
    timer.start(interval_ms)
    loop.exec_()


# 定义一个函数，用于获取系统信息
def system_info():
    # 获取CPU信息
    cpuInfo = systemInfo.GetCpuConstants()
    # 获取内存信息
    memInfo = systemInfo.GetMemInfo()
    # 获取磁盘信息
    diskInfoRaw = systemInfo.GetDiskInfo()
    # 获取磁盘总大小
    diskInfo = diskInfoRaw[0]['size']['total']

    # 返回系统信息
    return (f"// SYSTEM SELF-TEST\nCPU_COUNT: {cpuInfo['cpu_count']}\nCPU_NAME: {cpuInfo['cpu_name']}\nCPU_CORES: "
            f"{cpuInfo['cpu_core']}\nCPU_THREADS: {cpuInfo['cpu_threads']}\nMEMORY: {memInfo['memTotal']} MB\n"
            f"DISK: {diskInfo} B\n// COMPLETE.")


class FadeEffectWithLoop:
    # 初始化FadeEffectWithLoop类，设置窗口、控件和动画时长
    def __init__(self, win, widget, duration=1000):
        self.widget = widget
        self.win = win
        self.effect = QGraphicsOpacityEffect(widget)
        self.widget.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(duration)

    # 淡入效果
    def fade_in(self):
        loop = QEventLoop(self.win)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.finished.connect(loop.exit)
        self.animation.start()
        loop.exec_()

    # 淡出效果
    def fade_out(self):
        loop = QEventLoop(self.win)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(loop.exit)
        self.animation.start()
        loop.exec_()

class Loading(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 设置字体
        font = QFont("Consolas", pointSize=15)
        self.setFont(font)
        self.label.setFont(font)
        # 设置布局
        self.setLayout(self.verticalLayout)
        # 设置标签文本
        self.label.setText("")
        # 当标签文本改变时，将光标移动到文本末尾
        self.label.textChanged.connect(lambda: self.label.moveCursor(QTextCursor.End))
        # 设置垂直滚动条和水平滚动条策略
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置文本1
        self.text1 = fr'''
//////////////////////////////////////////////
// copyright(C)A.K.A Hollow Deep Dive System
// Led by Helios Reserch Institute
// Author:BW
// deep_dive_prototype_v4.h
//////////////////////////////////////////////

    __  __         ____           ____ 
   / / / /        / __ \         / __ \
  / /_/ /        / / / /        / / / /
 / __  /   _    / /_/ /   _    / /_/ /
/_/ /_/   (_)  /_____/   (_)  /_____/


starting system boot sequence...
loading startup modules and execute initialization...
loading system modules...
loading system core libraries in to memory...
the system uuid is {uuid.uuid3(uuid.NAMESPACE_DNS, "hollow_deep_dive_system")}.
validate system uuid from remote server...
system uuid is valid.
loading system configuration...
system configuration loaded.
system core libraries loaded.
checking modules dependencies...
checking network modules...
checking thread-modules...
checking database modules...
checking file-modules...
checking main-computer-core...
checking user-interface-core...
checking system-core...
All modules dependencies are valid.
current version:
network-module: 1.0.0 (latest)
thread-module: 1.0.0 (latest)
database-module: 1.0.0 (latest)
file-module: 1.0.0 (new-version: 1.1.0, is-available: True)
main-computer-core: 1.0.0 (latest)
user-interface-core: 1.0.0 (latest)
system-core: 1.0.0 (latest)
checking modules dependencies complete.
module: file-module is outdated.
downloading new version of file-module...
downloading file-module complete.
updating file-module...
updating file-module complete.
reloading into memory...
reloading complete.
system modules loaded.
validate system version...
the system version is 1.0.0. (latest)
system version is valid.
System initialization complete.

starting system...
'''
        # 设置文本2
        self.text2 = r'''
//////////////////////////////////////////////
// copyright(C)A.K.A Hollow Deep Dive System
// Led by Helios Reserch Institute
// Author:BW
//////////////////////////////////////////////

confirm the system is initialized...
the main-computer-core has returned the system to the normal state.
confirmed the system initialization is completed currently.
ready to start the user-gui program...
execute function: StartUserGui()...
execution user-gui program...
user-gui program now running...
all system modules are loaded and running.
the system is now ready to use.
send signal to start the main-computer-core...

main-computer-core has started, no errors detected.
'''

    # 显示文本0
    def showText0(self):
        # 获取系统信息
        text0 = system_info()
        # 在标签中滚动显示文本
        scroll_text_in_label(self, self.label, text0, 1000)
        # 播放声音
        player = ctypes.windll.kernel32
        player.Beep(3000, 500)
        # 创建事件循环
        loop = QEventLoop(self)
        # 清空标签文本
        self.label.setText("")
        # 设置定时器，2秒后退出事件循环
        QTimer.singleShot(2000, loop.quit)
        # 执行事件循环
        loop.exec()
        # 创建事件循环
        loop = QEventLoop(self)
        # 设置定时器，1秒后退出事件循环
        QTimer.singleShot(1000, loop.quit)
        # 执行事件循环
        loop.exec()

    # 显示文本1
    def showText1(self):
        # 在标签中滚动显示文本
        scroll_text_in_label(self, self.label, self.text1, 100)
        # 创建事件循环
        loop = QEventLoop(self)
        # 设置定时器，100毫秒后退出事件循环
        QTimer.singleShot(100, loop.quit)
        # 执行事件循环
        loop.exec()

    # 显示文本2
    def showText2(self):
        # 在标签中滚动显示文本
        scroll_text_in_label(self, self.label, self.text2, 100)
        # 创建事件循环
        loop = QEventLoop(self)
        # 设置定时器，1秒后退出事件循环
        QTimer.singleShot(1000, loop.quit)
        # 执行事件循环
        loop.exec()
        # 在标签中滚动显示文本
        scroll_text_in_label(self, self.label, "\n \n \nsystem boot complete, starting user-gui...", 500)
        # 创建事件循环
        loop = QEventLoop(self)
        # 设置定时器，300毫秒后退出事件循环
        QTimer.singleShot(300, loop.quit)
        # 执行事件循环
        loop.exec()

class showIcon(QWidget, Ui_Icon):
    # 定义一个showIcon类，继承自QWidget和Ui_Icon
    def __init__(self):
        # 初始化函数
        super().__init__()
        # 调用父类的初始化函数
        self.setupUi(self)
        # 调用setupUi函数，设置界面
        self.setLayout(self.verticalLayout)
        # 设置布局为verticalLayout


class MainPage(QWidget, Ui_MainPage):
    # 定义一个MainPage类，继承自QWidget和Ui_MainPage
    def __init__(self):
        # 初始化函数
        super().__init__()
        # 调用父类的初始化函数
        self.setupUi(self)
        # 调用setupUi函数，设置界面
        font_id1 = QFontDatabase.addApplicationFont("res/font/black.ttf")
        # 添加字体文件
        self.font_name1 = QFontDatabase.applicationFontFamilies(font_id1)[0]
        # 获取字体文件名
        font = QFont(self.font_name1, pointSize=18)
        # 设置字体
        self.setFont(font)
        # 设置界面字体
        self.label.setFont(QFont(self.font_name1, pointSize=130))
        # 设置label字体
        self.exeButton.setFont(font)
        # 设置exeButton字体
        self.toButton.setFont(font)
        # 设置toButton字体
        self.aboutButton.setFont(font)
        # 设置aboutButton字体
        self.exitButton.setFont(font)
        # 设置exitButton字体
        self.setLayout(self.verticalLayout)
        # 设置布局为verticalLayout
        self.verticalLayout.setContentsMargins(50, 20, 20, 20)
        # 设置布局的边距
        self.label.setText("")
        # 设置label文本为空
        pygame.mixer.init()
        # 初始化pygame的混音器
        pygame.mixer.music.set_volume(0.5)
        # 设置混音器的音量为0.5

    def onLabel(self):
        # 设置标签文本为"欢_"
        self.label.setText("欢_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎_"
        self.label.setText("欢迎_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎,_"
        self.label.setText("欢迎,_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，1500毫秒后退出事件循环
        QTimer.singleShot(1500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎,「_"
        self.label.setText("欢迎,「_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎,「法_"
        self.label.setText("欢迎,「法_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎,「法厄_"
        self.label.setText("欢迎,「法厄_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎,「法厄同_"
        self.label.setText("欢迎,「法厄同_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎,「法厄同」_"
        self.label.setText("欢迎,「法厄同」_")
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()
        # 设置标签文本为"欢迎,「法厄同」！"
        self.label.setText("欢迎,「法厄同」！")
        loop = QEventLoop(self)
        # 单次定时器，500毫秒后退出事件循环
        QTimer.singleShot(500, loop.quit)
        # 执行事件循环
        loop.exec()

    @staticmethod
    def startPlay():
        # 加载音乐文件
        pygame.mixer.music.load("res/sound/zzzExplorer.mp3")
        # 播放音乐，设置淡入时间为3000毫秒，循环播放
        pygame.mixer.music.play(fade_ms=3000, loops=-1)

    @staticmethod
    def stopPlay():
        # 淡出音乐，设置淡出时间为1000毫秒
        pygame.mixer.music.fadeout(1000)
        # 1秒后停止播放音乐
        QTimer.singleShot(1000, pygame.mixer.music.stop)

    @staticmethod
    def startPlayBattle():
        # 加载音乐文件
        pygame.mixer.music.load("res/sound/zzzBattle.mp3")
        # 播放音乐，设置淡入时间为500毫秒，循环播放
        pygame.mixer.music.play(fade_ms=500, loops=-1)

    @staticmethod
    def stopPlayBattle():
        # 淡出音乐，设置淡出时间为500毫秒
        pygame.mixer.music.fadeout(500)
        # 0.5秒后停止播放音乐
        QTimer.singleShot(500, pygame.mixer.music.stop)

    def paintEvent(self, a0):
        # 创建一个QPainter对象
        painter = QPainter(self)
        # 绘制一个矩形
        painter.drawRect(self.rect())
        # 加载图片文件
        pixmap = QPixmap("res/img/bg.png")  # 换成自己的图片的相对路径
        # 在矩形内绘制图片
        painter.drawPixmap(self.rect(), pixmap)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        # 定义一个变量quickFade，用于存储快速淡出效果
        self.quickFade = None
        # 调用user32.dll库
        self.u32 = ctypes.windll.user32
        # 应用暗色主题
        apply_style(self, "dark")
        # 设置窗口标题
        self.setWindowTitle("H.D.D.System")
        # 初始化调色板
        self.init_palette()
        # 创建一个堆叠窗口
        self.container = QStackedWidget(self)
        # 设置窗口中央部件
        self.setCentralWidget(self.container)
        # 全屏显示窗口
        self.showFullScreen()
        # 设置窗口图标
        self.setWindowIcon(QIcon("res/Icon.ico"))
        # 创建一个淡出效果
        self.fade = FadeEffectWithLoop(self, self.container)

        # 创建一个加载界面
        self.load = Loading()
        # 将加载界面添加到堆叠窗口中
        self.container.addWidget(self.load)

        # 创建一个图标界面
        self.icon = showIcon()
        # 将图标界面添加到堆叠窗口中
        self.container.addWidget(self.icon)

        # 创建一个主界面
        self.main = MainPage()
        # 将主界面添加到堆叠窗口中
        self.container.addWidget(self.main)
        # 将主界面的exeButton按钮的点击事件与onError函数连接
        self.main.exeButton.clicked.connect(self.onError)

        # 创建一个错误界面
        self.error = errorScreen()
        # 将错误界面添加到堆叠窗口中
        self.container.addWidget(self.error)
        # 将错误界面的backButton按钮的点击事件与onBack函数连接
        self.error.backButton.clicked.connect(self.onBack)

        # 创建一个加载界面
        self.loading = loadingScreen()
        # 将加载界面添加到堆叠窗口中
        self.container.addWidget(self.loading)

        # 创建一个关于界面
        self.about = aboutScreen()
        # 将关于界面添加到堆叠窗口中
        self.container.addWidget(self.about)
        # 将关于界面的backButton按钮的点击事件与onBack_函数连接
        self.about.backButton.clicked.connect(self.onBack_)
        # 将主界面的aboutButton按钮的点击事件与onAbout函数连接
        self.main.aboutButton.clicked.connect(self.onAbout)

        # 创建一个退出界面
        self.exit = exitScreen()
        # 将退出界面添加到堆叠窗口中
        self.container.addWidget(self.exit)
        # 将退出界面的backButton_2按钮的点击事件与onBack_函数连接
        self.exit.backButton_2.clicked.connect(self.onBack_)
        # 将主界面的exitButton按钮的点击事件与onExit函数连接
        self.main.exitButton.clicked.connect(self.onExit)

        # 将主界面的toButton按钮的点击事件与onWeb函数连接
        self.main.toButton.clicked.connect(self.onWeb)

        # 将堆叠窗口的当前界面设置为加载界面
        self.container.setCurrentWidget(self.load)
        # 显示加载界面的文本
        self.load.showText0()
        self.load.showText1()
        self.load.showText2()
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 设置一个定时器，1秒后退出事件循环
        QTimer.singleShot(1000, loop.quit)
        # 执行事件循环
        loop.exec()
        # 执行淡出效果
        self.fade.fade_out()
        # 将堆叠窗口的当前界面设置为图标界面
        self.container.setCurrentWidget(self.icon)
        # 执行淡入效果
        self.fade.fade_in()
        # 创建一个事件循环
        loop = QEventLoop(self)
        # 设置一个定时器，3秒后退出事件循环
        QTimer.singleShot(3000, loop.quit)
        # 执行事件循环
        loop.exec()
        # 执行淡出效果
        self.fade.fade_out()
        # 将堆叠窗口的当前界面设置为主界面
        self.container.setCurrentWidget(self.main)
        # 执行淡入效果
        self.fade.fade_in()
        # 执行主界面的startPlay函数
        self.main.startPlay()
        # 执行主界面的onLabel函数
        self.main.onLabel()

    def onError(self):
        # 播放错误音效
        self.playSound()
        # 如果quickFade为空，则创建一个FadeEffectWithLoop对象
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 停止播放主界面
        self.main.stopPlay()
        # 在1.5秒后开始播放战斗界面
        QTimer.singleShot(1500, self.main.startPlayBattle)
        # 执行淡出效果
        self.quickFade.fade_out()
        # 将容器设置为loading界面
        self.container.setCurrentWidget(self.loading)
        # 执行淡入效果
        self.quickFade.fade_in()
        # 创建一个事件循环，在10秒后退出
        loop = QEventLoop(self)
        QTimer.singleShot(10000, loop.quit)
        loop.exec()
        # 执行淡出效果
        self.quickFade.fade_out()
        # 将容器设置为error界面
        self.container.setCurrentWidget(self.error)
        # 执行淡入效果
        self.quickFade.fade_in()

    def onBack(self):
        # 播放返回音效
        self.playSound()
        # 如果quickFade为空，则创建一个FadeEffectWithLoop对象
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 停止播放战斗界面
        self.main.stopPlayBattle()
        # 执行淡出效果
        self.quickFade.fade_out()
        # 将容器设置为main界面
        self.container.setCurrentWidget(self.main)
        # 执行淡入效果
        self.quickFade.fade_in()
        # 如果main界面的label文本不是"欢迎,「法厄同」_"，则将其设置为"欢迎,「法厄同」_"
        if self.main.label.text() != "欢迎,「法厄同」！":
            self.main.label.setText("欢迎,「法厄同」！")

        # 开始播放主界面
        self.main.startPlay()

    def onBack_(self):
        # 播放声音
        self.playSound()
        # 如果quickFade为空，则创建一个FadeEffectWithLoop对象
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 执行淡出效果
        self.quickFade.fade_out()
        # 将当前窗口设置为main
        self.container.setCurrentWidget(self.main)
        # 执行淡入效果
        self.quickFade.fade_in()
        # 如果main窗口的label文本不是"欢迎,「法厄同」_"，则将其设置为"欢迎,「法厄同」_"
        if self.main.label.text() != "欢迎,「法厄同」！":
            self.main.label.setText("欢迎,「法厄同」！")

    def onAbout(self):
        # 播放声音
        self.playSound()
        # 如果quickFade为空，则创建一个FadeEffectWithLoop对象
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 执行淡出效果
        self.quickFade.fade_out()
        # 将当前窗口设置为about
        self.container.setCurrentWidget(self.about)
        # 执行淡入效果
        self.quickFade.fade_in()

    def onExit(self):
        # 播放声音
        self.playSound()
        # 如果quickFade为空，则创建一个FadeEffectWithLoop对象
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 执行淡出效果
        self.quickFade.fade_out()
        # 将当前窗口设置为exit
        self.container.setCurrentWidget(self.exit)
        # 执行淡入效果
        self.quickFade.fade_in()

    def onWeb(self):
        # 播放声音
        self.playSound()
        # 打开网页
        webbrowser.open("https://baike.mihoyo.com/zzz/wiki/")

    def closeEvent(self, a0, QCloseEvent=None):
        # 退出程序
        sys.exit()

    @staticmethod
    def playSound():
        threading.Thread(target=lambda: winsound.PlaySound("res/sound/click.wav", SND_ASYNC)).start()

    def init_palette(self):
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.setPalette(palette)


class errorScreen(QWidget, Ui_error):
    def __init__(self):
        super().__init__()
        # 设置界面
        self.setupUi(self)
        # 设置布局
        self.setLayout(self.verticalLayout)
        # 添加字体
        font_id1 = QFontDatabase.addApplicationFont("res/font/black.ttf")
        # 获取字体名称
        self.font_name1 = QFontDatabase.applicationFontFamilies(font_id1)[0]
        # 设置字体
        font = QFont(self.font_name1, pointSize=18)
        self.setFont(font)
        self.backButton.setFont(font)
        # 获取公网IP
        pubIP = requests.get("https://ident.me", proxies={'http': None, 'https': None}, timeout=10).text.strip()
        # 替换提示信息中的IP地址
        self.noticeLabel.setText(self.noticeLabel.text().replace("{ip}", f" [{pubIP}] "))

    def paintEvent(self, a0):
        # 绘制界面
        painter = QPainter(self)
        painter.drawRect(self.rect())
        # 加载背景图片
        pixmap = QPixmap("res/img/bg.png")
        # 绘制背景图片
        painter.drawPixmap(self.rect(), pixmap)


class loadingScreen(QWidget, Ui_loading):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        # 添加字体
        font_id1 = QFontDatabase.addApplicationFont("res/font/black.ttf")
        # 获取字体名称
        self.font_name1 = QFontDatabase.applicationFontFamilies(font_id1)[0]
        # 设置字体
        font = QFont(self.font_name1, pointSize=18)
        self.setFont(font)

    def paintEvent(self, a0):
        # 创建画笔
        painter = QPainter(self)
        # 绘制矩形
        painter.drawRect(self.rect())
        # 加载图片
        pixmap = QPixmap("res/img/bg.png") 
        # 绘制图片
        painter.drawPixmap(self.rect(), pixmap)


class aboutScreen(QWidget, Ui_about):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        self.moreInfoButton.clicked.connect(self.moreInfo)
        # 添加字体
        font_id1 = QFontDatabase.addApplicationFont("res/font/black.ttf")
        self.font_name1 = QFontDatabase.applicationFontFamilies(font_id1)[0]
        font = QFont(self.font_name1, pointSize=18)
        self.setFont(font)
        self.backButton.setFont(font)
        self.moreInfoButton.setFont(font)

    def moreInfo(self):
        self.moreInfoButton.close()
        # 设置文本
        text = ("""<html><head/><body><p>Hollow Deep Dive System</p>
            <p>Copyright ©A.K.A. </p>
            <p>Led by Helios Research Institute.</p>
            <p>Author: BW</p>
            <p>魔改人：太卜『符玄』</p>
            <p>魔改人主页：<a href="https://space.bilibili.com/1484496587"><span  style=" text-decoration: underline; color:#d36dde;">太卜『符玄』的个人空间</span></a></p>
            <p>原作者：Pickup_拾柒</p>
            <p>原作者的主页：<a href="space.bilibili.com/1638525867"><span  style=" text-decoration: underline; color:#a6c100;">Pickup_拾柒的个人空间</span></a></p></body></html>""")
        self.label_2.setText(text)

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.drawRect(self.rect())
        # 绘制背景图片
        pixmap = QPixmap("res/img/bg.png")  # 换成自己的图片的相对路径
        painter.drawPixmap(self.rect(), pixmap)

class exitScreen(QWidget, Ui_exit):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        # 添加字体
        font_id1 = QFontDatabase.addApplicationFont("res/font/black.ttf")
        self.font_name1 = QFontDatabase.applicationFontFamilies(font_id1)[0]
        font = QFont(self.font_name1, pointSize=18)
        self.setFont(font)
        # 连接退出按钮的点击事件
        self.exitButton.clicked.connect(sys.exit)
        # 设置退出按钮的字体
        self.exitButton.setFont(font)
        # 设置返回按钮的字体
        self.backButton_2.setFont(font)

    def paintEvent(self, a0):
        # 绘制窗口
        painter = QPainter(self)
        painter.drawRect(self.rect())
        # 绘制背景图片
        pixmap = QPixmap("res/img/bg.png")  # 换成自己的图片的相对路径
        painter.drawPixmap(self.rect(), pixmap)


if __name__   == '__main__':
    app = QApplication([])
    window = Main()
    window.show()
    app.exec()
