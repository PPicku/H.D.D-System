# -*- coding: utf-8 -*-
# 原代码作者为Github用户PPicku
# 该版本代码为Github用户NAAAAAAAAA1212
# 主要更改为：
# - 增加跨平台运行
# - 优化部分代码

import sys
import threading
import webbrowser
import requests
import platform  # 用于检测操作系统
import psutil    # 跨平台系统信息获取
import os
import subprocess
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QFontDatabase, QTextCursor, QPainter, QPixmap, QIcon
from PyQt5.QtWidgets import *
import pygame    # 用于音频播放

# 根据平台导入特定库
if platform.system() == "Windows":
    # Windows特有库
    import ctypes
    import winsound
    from winsound import *
    try:
        from pywinstyles import apply_style  # Windows界面美化
    except ImportError:
        print("警告：pywinstyles库不可用，界面样式将使用默认")
else:
    # macOS不需要这些库
    pass

# 导入UI文件（由PyQt Designer生成）
from hddLoading import Ui_Form
from Icon import Ui_Icon
from MainPage import Ui_MainPage
from errorScreen import Ui_error
from loadingScreen import Ui_loading
from aboutScreen import Ui_about
from exitScreen import Ui_exit

# 全局变量：主界面显示的文本
name = "欢迎，「法厄同」_"

# 资源路径处理函数（用于PyInstaller打包后访问资源）
def resource_path(relative_path):
    """获取资源的绝对路径，用于PyInstaller打包"""
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        # 当前文件所在目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 在QTextEdit中逐行滚动显示文本的函数
def scroll_text_in_label(win, label: QTextEdit, text_lines: str, interval_ms: int = 1000):
    """
    在QTextEdit控件中逐行显示文本
    
    参数:
        win: 父窗口
        label: 文本显示控件
        text_lines: 要显示的文本内容
        interval_ms: 行显示间隔(毫秒)
    """
    current_line = 0
    text_lines = text_lines.split("\n")

    # 创建定时器  
    timer = QTimer(win)

    # 定时器超时时的回调函数  
    loop = QEventLoop(win)

    def on_timeout():
        nonlocal current_line
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

# 获取系统信息（跨平台实现）
def system_info():
    """
    获取并返回系统信息字符串
    
    返回:
        格式化的系统信息字符串
    """
    # 跨平台获取CPU信息
    cpu_info = platform.processor()
    
    # 获取CPU核心数
    try:
        cpu_count = psutil.cpu_count(logical=False)  # 物理核心
        cpu_threads = psutil.cpu_count(logical=True)  # 逻辑核心/线程
    except:
        cpu_count = "N/A"
        cpu_threads = "N/A"
    
    # 获取内存信息
    try:
        mem = psutil.virtual_memory()
        mem_total = f"{mem.total // (1024 * 1024)} MB"  # 转换为MB
    except:
        mem_total = "N/A"
    
    # 获取磁盘信息（平台相关路径）
    try:
        # Windows使用C盘，macOS使用根目录
        disk_path = 'C:\\' if platform.system() == "Windows" else '/'
        disk = psutil.disk_usage(disk_path)
        disk_total = f"{disk.total // (1024 * 1024 * 1024)} GB"  # 转换为GB
    except:
        disk_total = "N/A"

    # 苹果芯片特殊处理
    if platform.system() != "Windows" and cpu_info == "arm":
        cpu_info = "Apple Silicon"

    # 返回格式化系统信息
    return (f"// SYSTEM SELF-TEST\nCPU: {cpu_info}\nCPU_CORES: {cpu_count}\n"
            f"CPU_THREADS: {cpu_threads}\nMEMORY: {mem_total}\n"
            f"DISK: {disk_total}\n// COMPLETE.")

# 淡入淡出效果类（带事件循环）
class FadeEffectWithLoop:
    """实现带事件循环的淡入淡出效果"""
    
    def __init__(self, win, widget, duration=1000):
        """
        初始化淡入淡出效果
        
        参数:
            win: 父窗口
            widget: 应用效果的控件
            duration: 动画时长(毫秒)
        """
        self.widget = widget
        self.win = win
        self.effect = QGraphicsOpacityEffect(widget)
        self.widget.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(duration)

    def fade_in(self):
        """淡入效果"""
        loop = QEventLoop(self.win)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.finished.connect(loop.exit)
        self.animation.start()
        loop.exec_()

    def fade_out(self):
        """淡出效果"""
        loop = QEventLoop(self.win)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(loop.exit)
        self.animation.start()
        loop.exec_()

# 加载界面（显示启动信息的界面）
class Loading(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 设置字体：Windows用Consolas，macOS用Menlo
        font_name = "Consolas" if platform.system() == "Windows" else "Menlo"
        font = QFont(font_name, pointSize=15)
        self.setFont(font)
        self.label.setFont(font)
        # 设置布局
        self.setLayout(self.verticalLayout)
        # 设置标签文本
        self.label.setText("")
        # 当标签文本改变时，将光标移动到文本末尾
        self.label.textChanged.connect(lambda: self.label.moveCursor(QTextCursor.End))
        # 隐藏滚动条
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 预定义显示文本（模拟代码）
        self.text1 = '''
//////////////////////////////////////////////
// copyright(C)A.K.A Hollow Deep Dive System
// Led by Helios Reserch Institute
// Author:BW
// deep_dive_prototype_v4.h
//////////////////////////////////////////////

#ifndef DEEP_DIVE_PROTOTYPE_V4_H
#define DEEP_DIVE_PROTOTYPE_V4_H
#include <MAP>
#include <helios_signal.h>
namespace Hollow
{
    class DeepDivePrototypeV4 : public DeepDiveBase:
    {
        private:
            HELIOS::BangbooHandle m_handle
            HChessboardMap<EHDomainType.EHSensorType> m_crossDomainSensorMap;
            HSensorContainer<VisualSensor> m_visualSensorContainer;

        public:
            virtual void RegisterBangbooHandle(HollowSignal signal) override;
            HCRESULI SyncVisualSensor(const HHatrics matWorld,HLINT hollowIndex);
    }
}
#endif // DEEP_DIVE_PROTOTYPE_V4_H'''
        self.text2 = '''
//////////////////////////////////////////////
// copyright(C)A.K.A Hollow Deep Dive System
// Led by Helios Reserch Institute
// Author:BW
//////////////////////////////////////////////

#include "deep_dive_prototype_v4.h"
#include "hollow_toolkit.h"
#include "hollow_boost.h"

namespace Hollow
{
    void DeepDivePrototypeV4::RegisterBangbooHandle(Hollowsignal signal)
    {
        if(m_initState != HollowInitState.HIS_DUCCESS)
            return;

        EHBoostType boostType = signal->GetBoostType();
        switch(boostType)
        {
            case EHBoostType.DEFAULT:
                m_handle = HELIOS::BangbooHandle.DEFAULT;
                break;

            case EHBoostType.ERROR:
                break;
        }
    }
}'''

    def showText0(self):
        """显示系统信息文本"""
        text0 = system_info()
        scroll_text_in_label(self, self.label, text0, 1000)
        
        # 平台相关声音提示
        if platform.system() == "Windows":
            try:
                # Windows播放声音
                player = ctypes.windll.kernel32
                player.Beep(3000, 500)
            except:
                pass
        else:
            # macOS播放声音
            try:
                subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
            except:
                pass
                
        # 等待2秒
        loop = QEventLoop(self)
        self.label.setText("")
        QTimer.singleShot(2000, loop.quit)
        loop.exec()
        
        # 再等待1秒
        loop = QEventLoop(self)
        QTimer.singleShot(1000, loop.quit)
        loop.exec()

    def showText1(self):
        """显示第一段模拟代码"""
        scroll_text_in_label(self, self.label, self.text1, 100)
        loop = QEventLoop(self)
        QTimer.singleShot(100, loop.quit)
        loop.exec()

    def showText2(self):
        """显示第二段模拟代码和启动完成信息"""
        scroll_text_in_label(self, self.label, self.text2, 100)
        loop = QEventLoop(self)
        QTimer.singleShot(1000, loop.quit)
        loop.exec()
        
        # 显示启动完成信息
        scroll_text_in_label(self, self.label, "\n \n \nSystem boot complete.", 500)
        loop = QEventLoop(self)
        QTimer.singleShot(300, loop.quit)
        loop.exec()

# 图标展示界面
class showIcon(QWidget, Ui_Icon):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)

# 主界面
class MainPage(QWidget, Ui_MainPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 加载字体文件
        font_path = resource_path("black.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            self.font_name = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Helvetica"
        else:
            # 平台默认字体
            self.font_name = "Helvetica" if platform.system() != "Windows" else "Consolas"
            
        # 设置字体
        font = QFont(self.font_name, pointSize=18)
        self.setFont(font)
        self.label.setFont(QFont(self.font_name, pointSize=130))
        self.exeButton.setFont(font)
        self.toButton.setFont(font)
        self.aboutButton.setFont(font)
        self.exitButton.setFont(font)
        
        # 设置布局
        self.setLayout(self.verticalLayout)
        self.verticalLayout.setContentsMargins(50, 20, 20, 20)
        self.label.setText("")
        
        # 初始化音频系统
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)

    def onLabel(self):
        """逐字符显示标题文本"""
        current_string = ""
        for char in name:
            if char != "_":
                current_string += char
            self.label.setText(current_string)
            # 每个字符显示间隔500毫秒
            loop = QEventLoop(self) 
            QTimer.singleShot(500, loop.quit)
            loop.exec()

    @staticmethod
    def startPlay():
        """播放主界面背景音乐"""
        try:
            pygame.mixer.music.load(resource_path("zzzExplorer.mp3"))
            pygame.mixer.music.play(fade_ms=3000, loops=-1)  # 淡入播放，循环
        except Exception as e:
            print(f"音乐播放失败: {e}")

    @staticmethod
    def stopPlay():
        """停止主界面音乐"""
        try:
            pygame.mixer.music.fadeout(1000)  # 淡出效果
            QTimer.singleShot(1000, pygame.mixer.music.stop)  # 确保停止
        except:
            pass

    @staticmethod
    def startPlayBattle():
        """播放战斗音乐"""
        try:
            pygame.mixer.music.load(resource_path("zzzBattle.mp3"))
            pygame.mixer.music.play(fade_ms=500, loops=-1)
        except Exception as e:
            print(f"战斗音乐播放失败: {e}")

    @staticmethod
    def stopPlayBattle():
        """停止战斗音乐"""
        try:
            pygame.mixer.music.fadeout(500)
            QTimer.singleShot(500, pygame.mixer.music.stop)
        except:
            pass

    def paintEvent(self, a0):
        """绘制背景图片"""
        painter = QPainter(self)
        painter.drawRect(self.rect())
        try:
            pixmap = QPixmap(resource_path("bg.png"))
            painter.drawPixmap(self.rect(), pixmap)
        except:
            # 出错时使用黑色背景
            painter.fillRect(self.rect(), Qt.black)

# 主窗口
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.quickFade = None  # 快速淡入淡出效果对象
        
        # 设置窗口属性
        self.setWindowTitle("H.D.D.System")
        
        # Windows平台应用暗色主题
        if platform.system() == "Windows":
            try:
                from pywinstyles import apply_style
                apply_style(self, "dark")
            except ImportError:
                print("界面美化不可用，使用默认样式")
        
        # 初始化界面颜色
        self.init_palette()
        
        # 创建堆叠窗口（用于多界面切换）
        self.container = QStackedWidget(self)
        self.setCentralWidget(self.container)
        self.showFullScreen()  # 全屏显示
        self.setWindowIcon(QIcon(resource_path("Icon.ico")))
        self.fade = FadeEffectWithLoop(self, self.container)  # 淡入淡出效果

        # 创建并添加各个界面
        self.load = Loading()
        self.container.addWidget(self.load)

        self.icon = showIcon()
        self.container.addWidget(self.icon)

        self.main = MainPage()
        self.container.addWidget(self.main)
        self.main.exeButton.clicked.connect(self.onError)  # 绑定按钮事件

        self.error = errorScreen()
        self.container.addWidget(self.error)
        self.error.backButton.clicked.connect(self.onBack)

        self.loading = loadingScreen()
        self.container.addWidget(self.loading)

        self.about = aboutScreen()
        self.container.addWidget(self.about)
        self.about.backButton.clicked.connect(self.onBack_)
        self.main.aboutButton.clicked.connect(self.onAbout)

        self.exit = exitScreen()
        self.container.addWidget(self.exit)
        self.exit.backButton_2.clicked.connect(self.onBack_)
        self.main.exitButton.clicked.connect(self.onExit)

        self.main.toButton.clicked.connect(self.onWeb)

        # 启动流程
        self.startup_sequence()

    def startup_sequence(self):
        """应用程序启动序列"""
        # 初始显示加载界面
        self.container.setCurrentWidget(self.load)
        self.load.showText0()  # 系统信息
        self.load.showText1()  # 模拟代码1
        self.load.showText2()  # 模拟代码2和启动完成
        
        # 等待1秒
        loop = QEventLoop(self)
        QTimer.singleShot(1000, loop.quit)
        loop.exec()
        
        # 切换到图标界面
        self.fade.fade_out()
        self.container.setCurrentWidget(self.icon)
        self.fade.fade_in()
        
        # 图标显示3秒
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()
        
        # 切换到主界面
        self.fade.fade_out()
        self.container.setCurrentWidget(self.main)
        self.fade.fade_in()
        self.main.startPlay()  # 播放主界面音乐
        self.main.onLabel()    # 显示动态文本

    def onError(self):
        """处理执行按钮点击事件（进入错误流程）"""
        self.playSound()
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 停止主音乐，准备战斗音乐
        self.main.stopPlay()
        QTimer.singleShot(1500, self.main.startPlayBattle)
        
        # 切换到加载中界面
        self.quickFade.fade_out()
        self.container.setCurrentWidget(self.loading)
        self.quickFade.fade_in()
        
        # 模拟10秒加载过程
        loop = QEventLoop(self)
        QTimer.singleShot(10000, loop.quit)
        loop.exec()
        
        # 切换到错误界面
        self.quickFade.fade_out()
        self.container.setCurrentWidget(self.error)
        self.quickFade.fade_in()

    def onBack(self):
        """从错误界面返回主界面"""
        self.playSound()
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 停止战斗音乐
        self.main.stopPlayBattle()
        
        # 返回主界面
        self.quickFade.fade_out()
        self.container.setCurrentWidget(self.main)
        self.quickFade.fade_in()
        
        # 恢复标题文本
        if self.main.label.text() != name:
            self.main.label.setText(name)

        # 播放主界面音乐
        self.main.startPlay()

    def onBack_(self):
        """从子界面（关于/退出）返回主界面"""
        self.playSound()
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 返回主界面
        self.quickFade.fade_out()
        self.container.setCurrentWidget(self.main)
        self.quickFade.fade_in()
        
        # 恢复标题文本
        if self.main.label.text() != name:
            self.main.label.setText(name)

    def onAbout(self):
        """进入关于界面"""
        self.playSound()
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 切换到关于界面
        self.quickFade.fade_out()
        self.container.setCurrentWidget(self.about)
        self.quickFade.fade_in()

    def onExit(self):
        """进入退出界面"""
        self.playSound()
        if not self.quickFade:
            self.quickFade = FadeEffectWithLoop(self, self.container, 250)

        # 切换到退出界面
        self.quickFade.fade_out()
        self.container.setCurrentWidget(self.exit)
        self.quickFade.fade_in()

    def onWeb(self):
        """打开网页"""
        self.playSound()
        webbrowser.open("https://baike.mihoyo.com/zzz/wiki/")

    def closeEvent(self, a0, QCloseEvent=None):
        """关闭应用程序"""
        sys.exit()

    def playSound(self):
        """播放点击音效（跨平台实现）"""
        if platform.system() == "Windows":
            # Windows使用winsound
            try:
                threading.Thread(
                    target=lambda: winsound.PlaySound(
                        resource_path("click.wav"), 
                        SND_ASYNC
                    )
                ).start()
            except:
                pass
        else:
            # macOS/Linux使用pygame或系统命令
            try:
                sound = pygame.mixer.Sound(resource_path("click.wav"))
                sound.play()
            except:
                try:
                    subprocess.run(["afplay", resource_path("click.wav")])
                except:
                    pass

    def init_palette(self):
        """初始化界面调色板（黑底白字）"""
        palette = QtGui.QPalette()
        # 设置活动状态颜色
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        
        # 设置非活动状态颜色
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        
        # 设置禁用状态颜色
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QBrush(QtGui.QColor(120, 120, 120)))
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QBrush(QtGui.QColor(120, 120, 120)))
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        
        self.setPalette(palette)

# 错误界面
class errorScreen(QWidget, Ui_error):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        
        # 设置字体
        font_path = resource_path("black.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_name = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Helvetica"
        else:
            font_name = "Helvetica" if platform.system() != "Windows" else "Consolas"
            
        font = QFont(font_name, pointSize=18)
        self.setFont(font)
        self.backButton.setFont(font)
        
        # 获取公网IP并显示
        try:
            pubIP = requests.get("https://ident.me", timeout=2).text.strip()
            self.noticeLabel.setText(self.noticeLabel.text().replace("{ip}", f" [{pubIP}] "))
        except:
            self.noticeLabel.setText(self.noticeLabel.text().replace("{ip}", " [IP获取失败] "))

    def paintEvent(self, a0):
        """绘制背景"""
        painter = QPainter(self)
        painter.drawRect(self.rect())
        try:
            pixmap = QPixmap(resource_path("bg.png"))
            painter.drawPixmap(self.rect(), pixmap)
        except:
            painter.fillRect(self.rect(), Qt.black)

# 加载中界面
class loadingScreen(QWidget, Ui_loading):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        
        # 设置字体
        font_path = resource_path("black.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_name = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Helvetica"
        else:
            font_name = "Helvetica" if platform.system() != "Windows" else "Consolas"
            
        font = QFont(font_name, pointSize=18)
        self.setFont(font)

    def paintEvent(self, a0):
        """绘制背景"""
        painter = QPainter(self)
        painter.drawRect(self.rect())
        try:
            pixmap = QPixmap(resource_path("bg.png"))
            painter.drawPixmap(self.rect(), pixmap)
        except:
            painter.fillRect(self.rect(), Qt.black)

# 关于界面
class aboutScreen(QWidget, Ui_about):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        self.moreInfoButton.clicked.connect(self.moreInfo)  # 绑定更多信息按钮
        
        # 设置字体
        font_path = resource_path("black.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_name = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Helvetica"
        else:
            font_name = "Helvetica" if platform.system() != "Windows" else "Consolas"
            
        font = QFont(font_name, pointSize=18)
        self.setFont(font)
        self.backButton.setFont(font)
        self.moreInfoButton.setFont(font)

    def moreInfo(self):
        """显示更多信息"""
        self.moreInfoButton.close()
        text = ('<html><head/><body><p>Hollow Deep Dive System</p><p>Copyright ©A.K.A. </p><p>Led by Helios Reserch '
                'Institute.</p><p>Author: BW</p><p>作者：Pickup_拾柒</p><p>作者主页：<a '
                'href="https://space.bilibili.com/1638525867"><span style=" text-decoration: underline; '
                'color:#a6c100;">Pickup_拾柒的个人空间</span></a></p>'
                '<p>增加MacOS运行部分作者：NAAAAAAAAA1212（GITHUB）</p><p>作者主页：<a '
                'href="https://github.com/NAAAAAAAAA1212"><span style=" text-decoration: underline; '
                'color:#a6c100;">NAAAAAAAAA1212 Github主页</span></a></p>'
                '<p>跨平台版本支持：Windows & macOS</p></body></html>')
        self.label_2.setText(text)

    def paintEvent(self, a0):
        """绘制背景"""
        painter = QPainter(self)
        painter.drawRect(self.rect())
        try:
            pixmap = QPixmap(resource_path("bg.png"))
            painter.drawPixmap(self.rect(), pixmap)
        except:
            painter.fillRect(self.rect(), Qt.black)

# 退出界面
class exitScreen(QWidget, Ui_exit):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        
        # 设置字体
        font_path = resource_path("black.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_name = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Helvetica"
        else:
            font_name = "Helvetica" if platform.system() != "Windows" else "Consolas"
            
        font = QFont(font_name, pointSize=18)
        self.setFont(font)
        self.exitButton.clicked.connect(sys.exit)  # 退出应用程序
        self.exitButton.setFont(font)
        self.backButton_2.setFont(font)

    def paintEvent(self, a0):
        """绘制背景"""
        painter = QPainter(self)
        painter.drawRect(self.rect())
        try:
            pixmap = QPixmap(resource_path("bg.png"))
            painter.drawPixmap(self.rect(), pixmap)
        except:
            painter.fillRect(self.rect(), Qt.black)

# 应用程序入口
if __name__ == "__main__":
    app = QApplication([])
    window = Main()
    window.show()
    app.exec()