# __author__: wangxupeng
# __QQ__: 857956556

import re

def get_mind_str(content, startstr, endstr):
    '''获取字符串的中间值
    '''
    s = re.search('%s.*%s' % (startstr, endstr), content)
    return s.group()

def to_sql(in_file_dir, out_file_dir):
    '''用于将tree.export_graphviz输出结果转换为标准sql
    in_file_dir: 输入文件路径C:/Users/85795/Desktop/tree_rule2.txt
    out_file_dir: 输出文件路径
    =========================
    tree.export_graphviz 参数说明
    为了能够准确的输出决策树规则，方法export_graphviz当中只能存在以下参数，且参数必须设置成
    以下形式。其余参数使用默认的即可。
    feature_names：特征名称，顺序必须和训练样本的数据一致
    class_names：类别名称，输入的时候，必须要排序。数据类型必须为str型的。不然会报错。
    filled：填充，必须为True
    node_ids：节点id，必须为True
    rounded：画的图形边缘是否美化，必须为True
    special_characters：必须为True
    =========================
    eg:
    --------     
    >>> import pandas as pd
    >>> import numpy as np
    >>> from sklearn import tree
    >>> from sklearn import metrics
    >>> from sklearn.model_selection import train_test_split
    >>> from sklearn.datasets import load_iris
	    
    >>> iris = load_iris()
    >>> clf = tree.DecisionTreeClassifier()
    >>> 
    >>> feature_names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    >>> data = pd.DataFrame(iris.data, columns=feature_names)
    >>> data['target'] = iris.target
	    
    >>> X_train, X_test, y_train, y_test = train_test_split(
    >>>                    data[feature_names], data['target'], test_size=0.33, random_state=42)
    >>> clf = clf.fit(data[feature_names], data['target'])
	## tree_rule.txt为输出文件的路径
	>>> tree.export_graphviz(model,out_file='tree_rule.txt',
    >>>                             feature_names=feture_selected_res,
    >>>                             class_names=['0', '1'],
    >>>                             filled=True,
    >>>                             node_ids=True,
    >>>                             rounded=True,
    >>>                             special_characters=True)
    
    >>> from graphviz_sql.extract import to_sql
	# tree_rule_2.txt: 通过决策树生成的用于graphviz画图的文件
	# tree_rule_2.sql: 转换后的sql文件
    >>> to_sql('tree_rule.txt', 'tree_rule_2.sql')
    '''

    with open(in_file_dir) as f:
        my_txt = f.readlines()
       
    # 获取索引
    my_txt_arrow = [i for i in my_txt if '->' in i]
    my_txt_node = [i for i in my_txt if 'label=<node' in i]
    
    my_txt_arrow = [i.split('[')[0] for i in my_txt_arrow]
    my_txt_arrow_split = [i.split('->') for i in my_txt_arrow]
    my_txt_arrow_split = [[re.findall('\d+', i[0])[0], 
                           re.findall('\d+', i[1])[0]] for i in my_txt_arrow_split]
    
    # 开始反转
    my_txt_arrow_split_reverse = my_txt_arrow_split[::-1]
    my_txt_arrow_split_reverse = [i[::-1] for i in my_txt_arrow_split_reverse]
    
    res = []
    for i in my_txt_arrow_split_reverse:
        res.extend([i[0], i[1]])
        
    
    my_txt_arrow_split_dct = {v[0]: v for v in my_txt_arrow_split_reverse}
    rever_idx = sorted(my_txt_arrow_split_dct.keys(),key=int, reverse=True)
    
    # 反向搜索
    rever_res = []
    for i in rever_idx:
        tmp_lst = []
        tmp_lst.append(i)
        while int(i) > 0:
            tmp_idx = my_txt_arrow_split_dct[i][1]  # 第一次
            tmp_lst.append(tmp_idx)
            i = tmp_idx              # 修正索引，直到搜索至0
        rever_res.append(tmp_lst) 
    
    tmp_rever_res = [','.join([str(j) for j in i]) for i in rever_res]
    # 判断后一个字符串是否为前一个字符串的子集，如果是，则剔除
    i = len(tmp_rever_res)-1
    while i > 0:
        if tmp_rever_res[i] in tmp_rever_res[i-1]:
            rv_val =  tmp_rever_res[i]
            tmp_rever_res.remove(rv_val)
        i -= 1
    
    index = [sorted(i.split(','), key=lambda x: int(x)) for i in tmp_rever_res]
    index_res = index[::-1]
    
    index_res2 = []
    for i in index_res:
        index_res2.append([int(j) for j in i])
    
    #index_res = [int(i) for i in index_res]
    
    del my_txt[0: 3]
    del my_txt[-1]
    my_txt[2] = my_txt[2][:my_txt[2].find('->')] + my_txt[2][my_txt[2].find('->'):6]+' ;'
    my_txt[4] = my_txt[2][:my_txt[4].find('->')] + my_txt[4][my_txt[4].find('->'):6]+' ;'
    
    # 整理数据
    msg_dict = {}
    for i, msg in enumerate(my_txt):
        msg_dict[i] = {}
        keys_idx = msg.find('[')
        if keys_idx == -1: 
    #        print(msg[: -1].split('->'))
            k_lst = [int(i) for i in msg[: keys_idx-1].split('->')]
            msg_dict[i]['keys'] = k_lst
        else:
    #        print(int(msg[: keys_idx-1]))
            try:
                msg_dict[i]['keys'] = [int(msg[: keys_idx-1])]
            except:
                # print(msg)
                k_lst = [int(i) for i in msg[: keys_idx-1].split('->')]
                msg_dict[i]['keys'] = k_lst
        try:
            _col = get_mind_str(msg, '<br/>', '&le')[5: -4]
            msg_dict[i]['col'] = _col
        except:
            msg_dict[i]['col'] = ''
        try:
            _val = get_mind_str(msg, '&le;', '<br/>gini')[5: -9]
            msg_dict[i]['val'] = _val
        except:
            msg_dict[i]['val'] = ''
        if '&le' in msg:
            _gin = get_mind_str(msg, 'gini = ', '<br/>s')[7: -6]
            msg_dict[i]['gini'] = _gin
        else:
            msg_dict[i]['gini'] = ''
        if '->' not in msg:
            _label = get_mind_str(msg, 'class = ', '>')[8: -1]
            msg_dict[i]['label'] = _label
        else:
            msg_dict[i]['label'] = ''
    
    
    
    idx_dct_val = {}
    i = 0
    for j in msg_dict.values():
        if len(j['keys']) == 1:
            idx_dct_val[i] = j
            i += 1
    
    res_sql = []
    for i in index_res2:
        tmp_s = []
        for j in range(len(i)):
            if idx_dct_val[i[j]]['col'] == '':
                break
            else:
                try:
                    if i[j+1] - i[j] > 1:  # 前后向判断，如果大于1，说明左分支变成右分支，变号
                        tmp_sql = idx_dct_val[i[j]]['col'] + ' > ' + idx_dct_val[i[j]]['val']
                    else:
                        tmp_sql = idx_dct_val[i[j]]['col'] + ' <= ' + idx_dct_val[i[j]]['val']
                except:
                    continue
            tmp_s.append(tmp_sql)
        res_sql.append(tmp_s)
    
    label_idx = [int(i[-1]) for i in index_res]
    label = []
    for i in label_idx:
        label.append(idx_dct_val[i]['label'])
    
    
    end = '0'
    sql_start = 'select case \n'
    sql_end = 'else ' + end + ' end;'
    
    result_sql = []
    result_sql.append(sql_start)
    
    for i in range(len(res_sql)):
        sql_ste = 'when ' + ' and '.join(res_sql[i]) + ' then ' + label[i] + ' \n'
        result_sql.append(sql_ste)
    result_sql.append(sql_end)
    
    
    with open(out_file_dir, 'w') as f:
        f.writelines(result_sql)
    print('...')
    print('=====wrirte sql success======')
    