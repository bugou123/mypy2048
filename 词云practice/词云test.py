# -*-  coding: utf-8 -*-

from wordcloud import WordCloud
import matplotlib.pyplot as plt

import numpy as np
from PIL import Image

import jieba

# 数据获取
with open('死了都要爱.txt', 'r',encoding = 'utf8')as f:
    text = f.read()

#图片获取
mask = np.array(Image.open('红心.jpg'))

# 数据清洗
# 屏蔽死了都要爱
STOPWORDS = []
STOPWORDS.append('死了都要爱')

font = r'C:\Windows\Fonts\simhei.ttf'
sep_list = jieba.lcut(text, cut_all = False)
sep_list = " ".join(sep_list)
wc = WordCloud(
    font_path = font,#使用的字体库
    margin = 2,
    mask = mask,#背景图片
    background_color = 'white', #背景颜色
    max_font_size = 200,
    min_font_size = 1,
    max_words = 200,
    stopwords = STOPWORDS, #屏蔽的内容
)

wc.generate(sep_list) #制作词云
wc.to_file('死了都要爱.jpg') #保存到当地文件

# 图片展示
plt.imshow(wc, interpolation = 'bilinear')
plt.axis('off')
plt.show()