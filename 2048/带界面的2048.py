# -*- coding: utf-8 -*-

import wx
import os
import random
import copy

class Frame(wx.Frame):

    def __init__(self,title):
        # 初始化，设置标题、默认 style
        super(Frame,self).__init__(None,-1,title,
                style = wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX^wx.RESIZE_BORDER)

        self.colors = {0:(204,192,179),2:(238, 228, 218),4:(237, 224, 200),
                8:(242, 177, 121),16:(245, 149, 99),32:(246, 124, 95),
                64:(246, 94, 59),128:(237, 207, 114),256:(237, 207, 114),
                512:(237, 207, 114),1024:(237, 207, 114),2048:(237, 207, 114)}
                
        # 设置图标
        self.setIcon()
        # 初始化游戏环境，字体、棋盘等
        self.initGame()
        # 定义缓冲区来画图
        self.initBuffer()
        # 创建面板
        panel = wx.Panel(self)
        # 绑定方法到键盘事件
        panel.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        panel.SetFocus()
        # 绑定触发事件的条件和函数方法
        self.Bind(wx.EVT_SIZE, self.onSize)  # use wx.BufferedPaintDC
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.SetClientSize((505,720))
        self.Center()
        self.Show()
    
    def onPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)
    
    def onClose(self, event):
        # 退出时保存分数
        self.saveScore()
        self.Destroy()

    def setIcon(self):
        # 设置图标
        icon = wx.Icon("icon.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    # 读取分数
    def loadScore(self):
        # 判断存储最高分数的文件是否存在
        if os.path.exists("bestscore.ini"):
            # 读取分数文件
            ff = open("bestscore.ini")
            self.bstScore = int(ff.read())
            ff.close()

    # 保存分数
    def saveScore(self):
        # 打开 bestscore.ini 文件，写入最高分
        ff = open("bestscore.ini","w")
        ff.write(str(self.bstScore))
        ff.close()

    def initGame(self):
        # 初始化字体
        self.bgFont = wx.Font(50, wx.SWISS, wx.NORMAL, wx.BOLD, face = u"Roboto")
        self.scFont = wx.Font(36, wx.SWISS, wx.NORMAL, wx.BOLD, face = u"Roboto")
        self.smFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, face = u"Roboto")
        self.curScore = 0
        self.bstScore = 0
        self.loadScore()
        # 定义象征棋盘的二维矩阵
        self.data = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
        count = 0
        # 随机生成 2 和 4，两次
        while count < 2:
            row = random.randint(0, len(self.data)-1)
            col = random.randint(0, len(self.data[0])-1)
            # 如果随机出的位置不等于 0 就跳过一次循环
            if self.data[row][col] != 0:
                continue
            self.data[row][col] = 2 if random.randint(0,1) else 4
            count += 1

    def initBuffer(self):
        # 得到应用窗口的宽和高
        w, h = self.GetClientSize()
        # 定义一块 buffer
        self.buffer = wx.EmptyBitmap(w,h)

    def onSize(self, event):
        # 当触发尺寸变换时调用
        self.initBuffer()
        self.drawAll()

    def putTile(self):
        available = []
        for row in range(len(self.data)):
            for col in range(len(self.data[0])):
                if self.data[row][col] == 0: available.append((row, col))
        if available:
            row,col = available[random.randint(0, len(available) - 1)]
            self.data[row][col] = 2 if random.randint(0, 1) else 4
            return True
        return False

    def slideUpDown(self, up):
        score = 0
        # 获取二维矩阵的长宽
        numCols = len(self.data[0])
        numRows = len(self.data)
        # 深度复制二位矩阵，存储到 oldData
        oldData = copy.deepcopy(self.data)

        for col in range(numCols):
            # 遍历找到不为零的数，即在棋盘上已经显示出来的数
            cvl = [self.data[row][col] for row in range(numRows) if self.data[row][col] != 0]

            if len(cvl)>=2:
                # 用 update 函数返回这一 direct（上、下、左、右） 的得分
                score += self.update(cvl, up)
            # 判断空出的位置补零
            for i in range(numRows - len(cvl)):
                if up:
                    # 在后面加零
                    cvl.append(0)
                else:
                    # 在前面加零
                    cvl.insert(0,0)
            # 更新棋盘
            for row in range(numRows):
                self.data[row][col] = cvl[row]
        return oldData != self.data, score

    def update(self, vlist, direct):
        score = 0
        if direct:  # up or left
            i = 1
            # 判断是否有相邻元素相等
            while i < len(vlist):
                if vlist[i-1] == vlist[i]:
                    # 删除相等相邻元素中的靠后元素
                    del vlist[i]
                    # 更新合并后的元素
                    vlist[i-1] *= 2
                    # 更新分数
                    score += vlist[i-1]
                    i += 1
                i += 1
        else:
            i = len(vlist)-1
            while i > 0:
                if vlist[i-1]==vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                    i -= 1
                i -= 1
        return score

    def slideLeftRight(self,left):
        score = 0
        numRows = len(self.data)
        numCols = len(self.data[0])
        oldData = copy.deepcopy(self.data)
        
        for row in range(numRows):
            rvl = [self.data[row][col] for col in range(numCols) if self.data[row][col]!=0]

            if len(rvl)>=2:           
                score += self.update(rvl,left)
            for i in range(numCols-len(rvl)):
                if left: rvl.append(0)
                else: rvl.insert(0,0)
            for col in range(numCols): self.data[row][col] = rvl[col]
        return oldData!=self.data,score

    def isGameOver(self):
        copyData = copy.deepcopy(self.data)

        flag = False
        # 当四个方向都无法移动时，GameOver
        if not self.slideUpDown(True)[0] and not self.slideUpDown(False)[0] and \
                not self.slideLeftRight(True)[0] and not self.slideLeftRight(False)[0]:
            flag = True
        # 还原 self.data
        if not flag: self.data = copyData
        return flag

    def doMove(self,move,score):
        if move:
            self.putTile()
            self.drawChange(score)
            if self.isGameOver():
                if wx.MessageBox(u"游戏结束，是否重新开始？",u"哈哈",
                        wx.YES_NO|wx.ICON_INFORMATION)==wx.YES:
                    bstScore = self.bstScore
                    self.initGame()
                    self.bstScore = bstScore
                    self.drawAll()

    # “↑ ↓ ← →”四个按键对应的棋盘处理方法
    def onKeyDown(self, event):
        # 获得键盘输入
        keyCode = event.GetKeyCode()
        # 对不同方向键作不同的处理
        if keyCode == wx.WXK_UP:
            self.doMove(*self.slideUpDown(True))
        elif keyCode == wx.WXK_DOWN:
            self.doMove(*self.slideUpDown(False))
        elif keyCode == wx.WXK_LEFT:
            self.doMove(*self.slideLeftRight(True))
        elif keyCode == wx.WXK_RIGHT:
            self.doMove(*self.slideLeftRight(False))        
                
    def drawBg(self,dc):
        dc.SetBackground(wx.Brush((250,248,239)))
        dc.Clear()
        dc.SetBrush(wx.Brush((187,173,160)))
        dc.SetPen(wx.Pen((187,173,160)))
        dc.DrawRoundedRectangle(15,150,475,475,5)

    def drawLogo(self,dc):
        dc.SetFont(self.bgFont)
        dc.SetTextForeground((119,110,101))
        dc.DrawText(u"2048",15,26)

    def drawLabel(self,dc):
        dc.SetFont(self.smFont)
        dc.SetTextForeground((119,110,101))
        dc.DrawText(u"合并相同数字，得到2048吧!",15,114)
        dc.DrawText(u"怎么玩: \n用-> <- 上下左右箭头按键来移动方块. \
                \n当两个相同数字的方块碰到一起时，会合成一个!",15,639)

    def drawScore(self,dc):            
        dc.SetFont(self.smFont)
        scoreLabelSize = dc.GetTextExtent(u"SCORE")
        bestLabelSize = dc.GetTextExtent(u"BEST")
        curScoreBoardMinW = 15*2+scoreLabelSize[0]
        bstScoreBoardMinW = 15*2+bestLabelSize[0]
        curScoreSize = dc.GetTextExtent(str(self.curScore))
        bstScoreSize = dc.GetTextExtent(str(self.bstScore))
        curScoreBoardNedW = 10+curScoreSize[0]
        bstScoreBoardNedW = 10+bstScoreSize[0]
        curScoreBoardW = max(curScoreBoardMinW,curScoreBoardNedW)
        bstScoreBoardW = max(bstScoreBoardMinW,bstScoreBoardNedW)
        dc.SetBrush(wx.Brush((187,173,160)))
        dc.SetPen(wx.Pen((187,173,160)))
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW,40,bstScoreBoardW,50,3)
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW-5-curScoreBoardW,40,curScoreBoardW,50,3)
        dc.SetTextForeground((238,228,218))
        dc.DrawText(u"BEST",505-15-bstScoreBoardW+(bstScoreBoardW-bestLabelSize[0])/2,48)
        dc.DrawText(u"SCORE",505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-scoreLabelSize[0])/2,48)
        dc.SetTextForeground((255,255,255))
        dc.DrawText(str(self.bstScore),505-15-bstScoreBoardW+(bstScoreBoardW-bstScoreSize[0])/2,68)
        dc.DrawText(str(self.curScore),505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-curScoreSize[0])/2,68)
    
    def drawTiles(self,dc):
        dc.SetFont(self.scFont)
        for row in range(4):
            for col in range(4):
                value = self.data[row][col]
                if value > 2048:
                    color = (237, 207, 114)
                else:
                    color = self.colors[value]
                if value==2 or value==4:
                    dc.SetTextForeground((119,110,101))
                else:
                    dc.SetTextForeground((255,255,255))
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                dc.DrawRoundedRectangle(30+col*115,165+row*115,100,100,2)
                size = dc.GetTextExtent(str(value))
                while size[0]>100-15*2:
                    self.scFont = wx.Font(self.scFont.GetPointSize()*4/5,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
                    dc.SetFont(self.scFont)
                    size = dc.GetTextExtent(str(value))
                if value!=0: dc.DrawText(str(value),30+col*115+(100-size[0])/2,165+row*115+(100-size[1])/2)

    def drawAll(self):
        # 使用 BufferedDC 来画图
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        self.drawBg(dc)
        self.drawLogo(dc)
        self.drawLabel(dc)
        self.drawScore(dc)
        self.drawTiles(dc)

    def drawChange(self,score):
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        if score:
            # 更新分数
            self.curScore += score
            # 更新最高分
            if self.curScore > self.bstScore:
                self.bstScore = self.curScore
            self.drawScore(dc)
        self.drawTiles(dc)

        
if __name__ == "__main__":
    app = wx.App()
    # 应用标题
    Frame(u"2048")
    app.MainLoop()
