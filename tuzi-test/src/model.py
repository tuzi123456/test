# -*- coding: utf-8 -*-
"""
# @Time    : 2018/5/26 下午5:03
# @Author  : zhanzecheng
# @File    : model.py
# @Software: PyCharm
"""
import math


class Node:
    """
    建立字典树的节点
    """

    def __init__(self, char):
        self.char = char
        # 记录是否完成
        self.word_finish = False
        # 用来计数
        self.count = 0
        # 用来存放节点
        self.child = {}
        # 判断是否是后缀
        self.isback = False


class TrieNode:
    """
    建立前缀树，并且包含统计词频，计算左右熵，计算互信息的方法
    """

    def __init__(self, node, data=None, PMI_limit=20):
        """
        初始函数，data为外部词频数据集
        :param node:
        :param data:外部词频数据集
        """
        self.root = Node(node)
        self.PMI_limit = PMI_limit
        if not data:
            return
        node = self.root
        for key, values in data.items():
            new_node = Node(key)
            new_node.count = int(values)
            new_node.word_finish = True
            if key not in node.child.keys():
                node.child[key] = new_node
            else:
                print('键值-' + key + '-已存在请检查导入词典文件')

    def add(self, word):
        """
        添加节点，对于左熵计算时，这里采用了一个trick，用a->b<-c 来表示 cba
        具体实现是利用 self.isback 来进行判断
        :param word:
        :return:
        """
        node = self.root
        # 正常加载
        for count, char in enumerate(word):
            # 在节点中找字符
            if char in node.child.keys():
                node = node.child[char]
                # node.found_in_child = True
            else:
                new_node = Node(char)
                node.child[char] = new_node
                node = new_node

            # 判断是否是最后一个节点
            if count == len(word) - 1:
                node.count += 1
                node.word_finish = True

        # 建立后缀表示
        length = len(word)
        node = self.root
        if length == 3:
            word[0], word[1], word[2] = word[1], word[2], word[0]
            for count, char in enumerate(word):
                found_in_child = False
                # 在节点中找字符
                if count != length - 1:
                    if char in node.child.keys():
                        node = node.child[char]
                        found_in_child = True
                else:
                    if char in node.child.keys() and node.child[char].isback:
                        node = node.child[char]
                        found_in_child = True

                if not found_in_child:
                    new_node = Node(char)
                    node.child[char] = new_node
                    node = new_node

                # 判断是否是最后一个节点
                if count == len(word) - 1:
                    node.count += 1
                    node.isback = True
                    node.word_finish = True

    def search_one(self):
        """
        寻找一阶共现，并返回词概率
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return False, 0
        total = 0
        for key in node.child.keys():
            if node.child[key].word_finish == True:
                total = total + node.child[key].count

        for key in node.child.keys():
            if node.child[key].word_finish == True:
                result[node.child[key].char] = node.child[key].count / total
        return result, total

    def search_right(self):
        """
        寻找右频次
        统计右熵，并返回右熵
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return False, 0

        for key in node.child.keys():
            child = node.child[key]
            for k in child.child.keys():
                cha = child.child[k]
                total = 0
                p = 0.0
                for k1 in cha.child.keys():
                    ch=cha.child[k1]
                    if ch.word_finish == True and not ch.isback:
                        total += ch.count
                for k1 in cha.child.keys():
                    ch=cha.child[k1]
                    if ch.word_finish == True and not ch.isback:
                        p += (ch.count / total) * math.log(ch.count / total, 2)
                result[child.char + cha.char] = -p
        return result

    def search_left(self):
        """
        寻找左频次
        统计左熵， 并返回左熵
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return False, 0

        for key in node.child.keys():
            child = node.child[key]
            for k in child.child.keys():
                cha = child.child[k]
                total = 0
                p = 0.0
                for k1 in cha.child.keys():
                    ch=cha.child[k1]
                    if ch.word_finish == True and ch.isback:
                        total += ch.count
                for k1 in cha.child.keys():
                    ch=cha.child[k1]
                    if ch.word_finish == True and ch.isback:
                        p += (ch.count / total) * math.log(ch.count / total, 2)
                result[child.char + cha.char] = -p

        return result

    def search_bi(self):
        """
        寻找二阶共现，并返回log2( P(X,Y) / (P(X) * P(Y))和词概率
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return False, 0

        total = 0
        # 寻找一阶共现，词概率
        one_dict, total_one = self.search_one()
        for key in node.child.keys():
            child = node.child[key]
            for k in child.child.keys():
                ch = child.child[k]
                if ch.word_finish == True:
                    total += ch.count
        for key in node.child.keys():
            child = node.child[key]
            for k in child.child.keys():
                ch = child.child[k]
                PMI = math.log(max(ch.count, 1), 2) - math.log(total, 2) - math.log(one_dict[child.char], 2) - math.log(
                    one_dict[ch.char], 2)
                # 这里做了PMI阈值约束
                if PMI > self.PMI_limit:
                    result[child.char + '_' + ch.char] = (PMI, ch.count / total)

        return result

    def wordFind(self, N):
        #  通过搜索得到互信息
        bi = self.search_bi()
        # 通过搜索得到左右熵
        left = self.search_left()
        right = self.search_right()
        result = {}
        for key, values in bi.items():
            d = "".join(key.split('_'))
            # 计算公式 score = PMI + min(左熵， 右熵)
            result[key] = (values[0] + min(left[d], right[d])) * values[1]

        result = sorted(result.items(), key=lambda x: x[1], reverse=True)
        dict_list = [result[0][0]]
        add_word = {}
        new_word = "".join(dict_list[0].split('_'))
        # 获得概率
        add_word[new_word] = result[0][1]

        # 取前5个
        for d in result[1:N]:
            flag = True
            for tmp in dict_list:
                pre = tmp.split('_')[0]
                if d[0].split('_')[-1] == pre or "".join(tmp.split('_')) in "".join(d[0].split('_')):
                    flag = False
                    break
            if flag:
                new_word = "".join(d[0].split('_'))
                add_word[new_word] = d[1]
                dict_list.append(d[0])

        return result, add_word
