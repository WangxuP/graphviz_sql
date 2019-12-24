# 将tree.export_graphviz构建决策树代码转换为标准sql
## 1. 工具简介
通常我们会采用`sklearn`框架`tree`模块进行决策树相关的挖掘分析，并使用`tree.export_graphviz`将决策树过程导出为`graphviz.dot`文件
再配合外部程序`graphviz`进行画图。  
但在有些时候，我们会根据决策树图形来抽取关键路径，将其翻译成标准`sql`，部署在数据库当中，持续化产生价值。  
目前`sklearn`暂未提供此功能，故我们开发此插件来进行完善。

## 2. 安装环境、依赖
- 安装方法:支持在线安装或离线安装
    - [download](https://pypi.org/manage/project/graphviz-sql/releases/)  
> pip install graphviz_sql
- 内部依赖
	- sklearn
- 外部依赖
	- [Graphviz](https://graphviz.gitlab.io/download/):找到适合自己版本下载即可



## 3. 一个简单的示例
#### 将`tree.export_graphviz`输出结果转换为标准`sql` 

**`tree.export_graphviz`参数说明**  
为了能够准确的输出决策树规则，方法`tree.export_graphviz`当中一下参数必须设置成以下形式。其余参数使用默认的即可。
- `feature_names`：特征名称，顺序必须和训练样本的数据一致  
- `class_names`：类别名称，输入的时候，必须要排序。如将原来的['1', '0']设置为['0', '1']，注意：数据类型必须为`str`型的。  
- `filled`：填充，必须为`True`  
- `node_ids`：节点id，必须为`True`  
- `rounded`：画的图形边缘是否美化，必须为`True`  
- `special_characters`：必须为`True`

=========================
### eg:
```python
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
iris = load_iris()
clf = tree.DecisionTreeClassifier()

feature_names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
data = pd.DataFrame(iris.data, columns=feature_names)
data['target'] = iris.target
X_train, X_test, y_train, y_test = train_test_split(
                   data[feature_names], data['target'], test_size=0.33, random_state=42)
clf = clf.fit(data[feature_names], data['target'])
# tree_rule_2.txt为输出文件的路径
tree.export_graphviz(model,out_file='tree_rule.dot',
                            feature_names=feture_selected_res,
                            class_names=['0', '1'],
                            filled=True,
                            node_ids=True,
                            rounded=True,
                            special_characters=True)


# 调用插件  
from graphviz_sql.extract import to_sql 

# tree_rule.dot: 通过决策树生成的用于graphviz画图的文件路径
# tree_rule_2.sql: 转换后的sql文件路径 
to_sql('tree_rule.dot', 'tree_rule_2.sql')
```
# 4. 代码原理
通过一种反向搜索的方法遍历决策树结果，将结果转换成标准sql
# 5. 常见问题说明
- 乱码
	- 此问题可百度一下，网上有具体的处理办法，
	- 其它问题请及时反馈
    
## 6. 加入进来
强大的工具需要你我共同完善，期待技术大佬的加入。

- email:
> wang_xup@163.com  
> 857956556@qq.com
    
