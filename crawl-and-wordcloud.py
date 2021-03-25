# encoding: UTF-8

from wordcloud import WordCloud # 生成云图
import matplotlib.pyplot as plt # 可视化展示
import matplotlib.colors as colors # 图片设置颜色
import jieba # 中文句子分词
from PIL import Image # 云图背景图处理
import numpy as np # 云图背景图处理，生成矩阵
import requests # 爬取数据
from lxml import etree # 解析获取的页面
import re # 匹配返回的数据

# 请求头
headers = { 
    'Referer' :'http://music.163.com', 
    'Host' :'music.163.com', 
    'Accept' :'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 
    'User-Agent':'Chrome/10' 
    }

# 等到歌手的页面 前50的歌曲ID，歌曲名
def get_songs(artist_id):
    page_url = 'https://music.163.com/artist?id=' + artist_id
    # 获取网页HTML
    res = requests.request('GET', page_url, headers = headers)
    # 用XPath解析 前50首热门歌曲
    html = etree.HTML(res.text)
    href_xpath = "//*[@id='hotsong-list']//a/@href" 
    name_xpath = "//*[@id='hotsong-list']//a/text()" 
    hrefs = html.xpath(href_xpath) 
    names = html.xpath(name_xpath) 
    # 设置热门歌曲的ID，歌曲名称 
    song_ids = [] 
    song_names = [] 
    for href, name in zip(hrefs, names): 
        song_ids.append(href[9:]) 
        song_names.append(name)  
    return song_ids, song_names

#得到一首歌的歌词
def get_song_lyric(headers, lyric_url):
    res = requests.request('GET', lyric_url, headers = headers)
    if 'lrc' in res.json():
        lyric = res.json()['lrc']['lyric']
        new_lyric = re.sub(r'[\d:.[\]]', '', lyric)
        return new_lyric
    else:
        return ''

# 生成词云
def create_word_cloud(words):
    print('根据词频，开始生成词云!')
    cut_text = ''.join(jieba.cut(words, cut_all = False, HMM = True))
    # 停用词
    stop_words = ['作词', '作曲', '曲', '编曲', 'Arranger', '录音', '混音', '人声', 'Vocal', '弦乐', 'Keyboard', '键盘', '编辑', '助理', 'Assistants', 'Mixing', 'Editing', 'Recording', '音乐', '制作', 'Producer', '发行', 'produced', 'and', 'distributed']
    wc = WordCloud(
        # 设置字体,注意路径,针对中文的情况需要设置中文字体，否则显示乱码。
        font_path="Hiragino Sans GB.ttc", 
        max_words=100, # 设置最大的字数
        width=800, # 设置画布的宽度
        height=600, # 设置画布的高度
        background_color='#DADADA',
        mask=np.array(Image.open('panda.jpg')), # 设置背景图片
        stopwords=stop_words, # 设置停用词 
        max_font_size=150, # 设置字体最大值 
        colormap=colors.ListedColormap(['#17223B','#263859','#6B778D', '#FF6768']),  # 指定颜色
    )
    wordcloud = wc.generate(cut_text)
    # 写词云图片  
    wordcloud.to_file("wordcloud.jpg")    
    # 显示词云文件    
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")    
    plt.show()

if __name__ == '__main__':
    # 设置歌手ID，毛不易为12138269
    artist_id = '29393033'
    [song_ids, song_names] = get_songs(artist_id)
    # 所有歌词
    all_word = ''
    # 获取每首歌歌词
    for (song_id, song_name) in zip(song_ids, song_names): 
        # 歌词API URL 
        lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + song_id + '&lv=-1&kv=-1&tv=-1' 
        lyric = get_song_lyric(headers, lyric_url) 
        all_word = all_word + ' ' + lyric 
        print('正在下载歌曲：' + song_name)
    #根据词频 生成词云
    create_word_cloud(all_word)  

