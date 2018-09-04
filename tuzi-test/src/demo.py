# -*- coding: utf-8 -*-
#https://github.com/zhanzecheng/Chinese_segment_augment
"""
# @Time    : 2018/5/26 下午5:13
# @Author  : zhanzecheng
# @File    : demo.py.py
# @Software: PyCharm
"""

from src.model import TrieNode
from src.utils import *
import jieba
import time
from sklearn.externals import joblib
s_time = time.time()
# 定义取TOP5个
N = 5

# 加载数据集
data = []
with open('../data/HZB.txt', 'r', encoding='utf8') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        line = [x for x in jieba.cut(line, cut_all=False) if x not in stopword]
        data.append(line)

time_elapse = time.time() - s_time
E_time = time.time()
print("Time Cost: {}s".format(time_elapse))

print('------> 初始化字典树')
root = TrieNode('*', word_freq)
joblib.dump(root,'ddd.bin')

time_elapse = time.time() - E_time
E_time = time.time()
print("Time Cost: {}s".format(time_elapse))

# print('------> 加载初始化字典树')
# root=joblib.load('ddd.bin')
# time_elapse = time.time() - E_time
# E_time = time.time()
# print("Time Cost: {}s".format(time_elapse))

print('------> 插入节点')
for i in data:
    tmp = generate_ngram(i, 3)
    for d in tmp:
        root.add(d)
time_elapse = time.time() - E_time
E_time = time.time()
print("Time Cost: {}s".format(time_elapse))
result, add_word = root.wordFind(50)

print('增加了%d个新词, 词语和得分分别为' % len(add_word))
print('#############################')
for word, score in add_word.items():
    print(word + ' ---->  ', score)
print('#############################')

# print('%d个词语和得分分别为' % len(result))
# print('#############################')
# for i in range(len(result)):
#     print(result[i])
# print('#############################')

# 如果想要调试和选择其他的阈值，可以print result来调整
# print(result)

test = '贷记卡设置自扣还款账号'
print('添加前：')
print("".join([(x + '/ ') for x in jieba.cut(test, cut_all=False) if x not in stopword]))

for word, score in add_word.items():
    jieba.add_word(word)
print("添加后：")
print("".join([(x + '/ ') for x in jieba.cut(test, cut_all=False) if x not in stopword]))

time_elapse = time.time() - s_time
print("Time Cost all: {}s".format(time_elapse))




