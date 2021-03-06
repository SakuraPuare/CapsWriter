# -*- coding: UTF-8 -*-

from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton
# from PySide2.QtGui import *
from PySide2.QtCore import Signal
import os, re, subprocess, time

import pyaudio


from moduels.component.NormalValue import 常量
from moduels.component.QEditBox_StdoutBox import QEditBox_StdoutBox
from moduels.thread.Thread_AliEngine import Thread_AliEngine
from moduels.gui.Combo_EngineList import Combo_EngineList


class Tab_CapsWriter(QWidget):
    状态栏消息 = Signal(str, int)

    def __init__(self):
        super().__init__()
        self.initElements()  # 先初始化各个控件
        self.initSlots()  # 再将各个控件连接到信号槽
        self.initLayouts()  # 然后布局
        self.initValues()  # 再定义各个控件的值


    def initElements(self):
        self.页面总布局 = QVBoxLayout()

        self.引擎选择Box = QGroupBox('引擎选择')
        self.引擎选择下拉框 = Combo_EngineList()
        self.引擎选择Box布局 = QVBoxLayout()

        self.控制台输出Box = QGroupBox('提示消息')
        self.控制台输出框 = QEditBox_StdoutBox()
        self.控制台输出Box布局 = QVBoxLayout()

        self.启停按钮Box = QGroupBox('开关')
        self.启动按钮 = QPushButton('启用 CapsWriter')
        self.停止按钮 = QPushButton('停止 CapsWriter')
        self.启停按钮Box布局 = QHBoxLayout()



    def initLayouts(self):


        self.引擎选择Box布局.addWidget(self.引擎选择下拉框)

        self.控制台输出Box布局.addWidget(self.控制台输出框)

        self.启停按钮Box布局.addWidget(self.启动按钮)
        self.启停按钮Box布局.addWidget(self.停止按钮)

        self.引擎选择Box.setLayout(self.引擎选择Box布局)
        self.控制台输出Box.setLayout(self.控制台输出Box布局)
        self.启停按钮Box.setLayout(self.启停按钮Box布局)

        self.页面总布局.addWidget(self.引擎选择Box)
        self.页面总布局.addWidget(self.控制台输出Box)
        self.页面总布局.addWidget(self.启停按钮Box)

        self.setLayout(self.页面总布局)

    def initSlots(self):
        self.启动按钮.clicked.connect(self.启动引擎)
        self.停止按钮.clicked.connect(self.停止引擎)

    def 更新控制台输出(self, 文本):
        self.控制台输出框.print(文本)

    def initValues(self):
        self.引擎线程 = None
        self.停止按钮.setDisabled(True)

        print("""\n软件介绍：

CapsWriter，顾名思义，就是按下大写锁定键来打字的工具。它的具体作用是：当你按下键盘上的大写锁定键后，软件开始语音识别，当你松开大写锁定键时，识别的结果就可以立马上屏。

目前软件内置了对阿里云一句话识别 API 的支持。如果你要使用，就需要先在阿里云上实名认证，申请语音识别 API，在设置页面添加一个语音识别引擎。

具体申请阿里云 API 的方法，可以参考我这个视频：https://www.bilibili.com/video/BV1qK4y1s7Fb/

添加上引擎后，在当前页面选择一个引擎，点击启用按钮，就可以进行语音识别了！嗯

启用后，在实际使用中，只要按下 CapsLock 键，软件就会立刻开始录音：

    如果只是单击 CapsLock 后松开，录音数据会立刻被删除；
    如果按下 CapsLock 键时长超过 0.3 秒，就会开始连网进行语音识别，松开 CapsLock 键时，语音识别结果会被立刻输入。

所以你只需要按下 CapsLock 键，无需等待，就可以开始说话，因为当你按下按下 CapsLock 键的时候，程序就开始录音了。说完后，松开，识别结果立马上屏。\r\n""")

    def 启动引擎(self):
        if self.引擎线程 != None: return
        引擎名称 = self.引擎选择下拉框.currentText()
        if 引擎名称 == '': return
        self.启动按钮.setDisabled(True)
        self.停止按钮.setEnabled(True)
        result = 常量.数据库连接.execute(f'''select * from {常量.语音引擎表单名} where 引擎名称 = :引擎名称''',
                                  {'引擎名称': 引擎名称}).fetchone()
        if result == None: return
        self.引擎线程 = Thread_AliEngine(引擎名称, self)
        self.引擎线程.识别中的信号.connect(常量.托盘.切换聆听中的图标)
        self.引擎线程.结束识别的信号.connect(常量.托盘.切换正常图标)
        self.引擎线程.引擎出错信号.connect(self.停止引擎)
        self.引擎线程.start()


    def 停止引擎(self):
        if self.引擎线程 != None:
            self.引擎线程.停止引擎()
            # print(self.引擎线程.isRunning())
            self.引擎线程 = None
            self.启动按钮.setEnabled(True)
            self.停止按钮.setDisabled(True)


        # self.压缩图片_按钮纵向布局.通过id勾选单选按钮(常量.输出选项['图片压缩'])
        # self.输出格式_按钮纵向布局.通过id勾选单选按钮(常量.输出选项['输出格式'])
        # self.其它_安装到手机选框.setChecked(常量.输出选项['adb发送至手机'])
        # self.其它_清理注释选框.setChecked(常量.输出选项['清理注释'])
    #
    # def 无线adb(self):
    #     self.无线adb线程.start()
    #
    # def 提取皮肤(self):
    #     self.提取皮肤线程.start()
    #
    # def 解压皮肤(self):
    #     解压皮肤对话框 = Dialog_DecompressSkin()
    #
    # def 发送皮肤(self):
    #     获得的皮肤路径 = QFileDialog.getOpenFileName(self, caption='选择皮肤', dir=常量.皮肤输出路径, filter='皮肤文件 (*.bds)')[0]
    #     if 获得的皮肤路径 == '': return True
    #     皮肤文件名 = os.path.basename(获得的皮肤路径)
    #     手机皮肤路径 = '/sdcard/baidu/ime/skins/' + 皮肤文件名
    #     发送皮肤命令 = f'''adb push "{获得的皮肤路径}" "{手机皮肤路径}"'''
    #     subprocess.run(发送皮肤命令, startupinfo=常量.subprocessStartUpInfo)
    #     安装皮肤命令 = f'''adb shell am start -a android.intent.action.VIEW -c android.intent.category.DEFAULT -n com.baidu.input/com.baidu.input.ImeUpdateActivity -d '{手机皮肤路径}' '''
    #     subprocess.run(安装皮肤命令, startupinfo=常量.subprocessStartUpInfo)
    #
    #
    # def 备份选中皮肤(self):
    #     if self.皮肤列表Box.列表.currentRow() < 0: return
    #     已选中的列表项 = self.皮肤列表Box.列表.currentItem().text()
    #     输出文件名, 皮肤源文件目录 = 常量.数据库连接.cursor().execute(
    #         f'select outputFileName, sourceFilePath from {常量.数据库皮肤表单名} where skinName = :皮肤名字;',
    #         {'皮肤名字': 已选中的列表项}).fetchone()
    #     备份时间 = time.localtime()
    #     备份压缩文件名 = f'{输出文件名}_备份_{备份时间.tm_year}年{备份时间.tm_mon}月{备份时间.tm_mday}日{备份时间.tm_hour}时{备份时间.tm_min}分{备份时间.tm_sec}秒.bds'
    #     备份文件完整路径 = os.path.join(常量.皮肤输出路径, '皮肤备份文件', 备份压缩文件名)
    #     备份命令 = f'''winrar a -afzip -ibck -r -ep1 "{备份文件完整路径}" "{皮肤源文件目录}/*"'''
    #     if not os.path.exists(os.path.dirname(备份文件完整路径)): os.makedirs(os.path.dirname(备份文件完整路径))
    #     subprocess.run(备份命令, startupinfo=常量.subprocessStartUpInfo)
    #     os.startfile(os.path.dirname(备份文件完整路径))
    #
    #
    # def 还原选中皮肤(self):
    #     if self.皮肤列表Box.列表.currentRow() < 0: return
    #     已选中的列表项 = self.皮肤列表Box.列表.currentItem().text()
    #     输出文件名, 皮肤源文件目录 = 常量.数据库连接.cursor().execute(
    #         f'select outputFileName, sourceFilePath from {常量.数据库皮肤表单名} where skinName = :皮肤名字;',
    #         {'皮肤名字': 已选中的列表项}).fetchone()
    #     备份文件夹路径 = os.path.join(常量.皮肤输出路径, '皮肤备份文件')
    #     Dialog_RestoreSkin(备份文件夹路径, 输出文件名, 皮肤源文件目录)
    #
    # def 打开皮肤输出文件夹(self):
    #     if not os.path.exists(常量.皮肤输出路径): os.makedirs(常量.皮肤输出路径)
    #     os.startfile(常量.皮肤输出路径)
    #
    # def 打包选中皮肤(self):
    #     if self.皮肤列表Box.列表.currentRow() < 0: return True
    #     self.备份选中皮肤_按钮.setDisabled(True)
    #     self.还原选中皮肤_按钮.setDisabled(True)
    #     self.打包选中皮肤_按钮.setDisabled(True)
    #     self.打包所有皮肤_按钮.setDisabled(True)
    #     self.生成皮肤线程.是否要全部生成 = False
    #     self.生成皮肤线程.start()
    #
    # def 打包所有皮肤(self):
    #     self.备份选中皮肤_按钮.setDisabled(True)
    #     self.还原选中皮肤_按钮.setDisabled(True)
    #     self.打包选中皮肤_按钮.setDisabled(True)
    #     self.打包所有皮肤_按钮.setDisabled(True)
    #     self.生成皮肤线程.是否要全部生成 = True
    #     self.生成皮肤线程.start()
    #
    # def 生成皮肤线程完成(self):
    #     self.备份选中皮肤_按钮.setEnabled(True)
    #     self.还原选中皮肤_按钮.setEnabled(True)
    #     self.打包选中皮肤_按钮.setEnabled(True)
    #     self.打包所有皮肤_按钮.setEnabled(True)
    #     常量.状态栏.showMessage('打包任务完成！', 5000)

