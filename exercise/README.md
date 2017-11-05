# DAND_OpenStreetMap
基于OpenStreetMap的数据清洗程序

# 小实验

### 标签类型

**tags.py**

问题描述

你的任务是进一步探索数据。

在处理数据并将其添加到数据库中之前，你应该检查每个“<标记>”的“k”值，看看是否存在潜在问题。

我们提供了 3 个正则表达式，用来检查标记的某些规律。正如在上一道测验中看到的，我们想要更改数据模型，并将“addr:street”类型的键展开为字典，如下所示：{"address": {"street": "Some value"}}

我们需要查看是否有此类标记，以及任何标记是否存在具有问题的字符。

请完成函数“key_type”，并得出这四大标记类别在字典中的各自数量：

“lower”，表示仅包含小写字母且有效的标记，
“lower_colon”，表示名称中有冒号的其他有效标记，
“problemchars”，表示字符存在问题的标记，以及
“other”，表示不属于上述三大类别的其他标记。
请参阅“process_map”和“test”函数，了解我们期望的格式。

要获得将正则表达式与 re 模块一起使用的帮助，请查看 [文档](https://docs.python.org/2/library/re.html)

### 练习: 探索用户

**users.py**

问题描述

你的任务是进一步探索数据。

第一项任务比较有趣，查找这一特定地区有多少唯一用户向地图做出了贡献！

函数 process_map 应该返回一组唯一的用户 ID（“uid”）

### 完善街道名

**audit.py**

问题描述

在这道练习中，你需要完成以下两步：

审核 OSMFILE 并更改变量“mapping”，表示为了修正预期列表中相应项的错误街道类型需要做出的更改。你必须仅为在此 OSMFILE 中发现的实际问题添加映射，而不是泛化的解决方案，因为这将取决于你要审核的特定区域。
编写 update_name 函数，实际地修正街道名称。该函数传入街道名称作为参数，应该返回修正过后的名称。我们提供了一个简单的测试，使你能够了解我们的预期结果

### 准备数据库 - MongoDB

**data.py**

问题描述

你的任务是处理数据并将数据形状变成我们之前提到的模型。输出应该是字典列表，如下所示：
```javascript
{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}
```
你需要完成函数 shape_element。

我们提供了用于解析地图文件的函数，并调用该函数，将元素作为参数。你应该返回一个字典，其中包含该元素的已调整形状的数据。我们还提供了将数据保存到文件中的方式，使你能够稍后使用 mongoimport 将已调整形状的数据导入到 MongoDB。

注意，在此练习中，我们不使用你在上一道练习中用到的“更新街道名称”流程。如果你在最终项目中使用该代码，强烈建议你使用上一道练习中的代码更新街道名称，然后将其保存到 JSON 中。

具体来说，你应该完成以下任务：

- 你应该只处理两种类型的顶级标记：“节点”和“道路”
- “节点”和“道路”应该转换为常规键值对，以下情况除外：
- - CREATED 数组中的属性应该添加到键“created”下
- - 经纬度属性应该添加到“pos”数组中，以用于地理空间索引编制。确保“pos”数组中的值是浮点型，不是字符串。
- 如果二级标记“k”值包含存在问题的字符，则应忽略
- 如果二级标记“k”值以“addr:”开头，则应添加到字典“address”中
- 如果二级标记“k”值不是以“addr:”开头，但是包含“:”，你可以按照自己认为最合适的方式进行处理。例如，你可以将其拆分为二级字典，例如包含“addr:”，或者转换“:”以创建有效的键。
- 如果有第二个用于区分街道类型/方向的“:”，则应该忽略该标记，例如：

```xml
<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>
```
应该改写为：
```javascript
{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}
```
对于道路（ways）
```xml
  <nd ref="305896090"/>
  <nd ref="1719825889"/>
```
应该改写为：
```javascript
"node_refs": ["305896090", "1719825889"]
```
如果您在自己的计算机上使用上述 process_map() 程序写入到 JSON 文件，请确保您通过 pretty = False 参数调用该程序。否则，在您尝试将 JSON 文件导入 MongoDB 时，mongoimport 可能会引发错误。

# MongoDB 清洗程序


