# OpenStreetMap Sample Project Data Wrangling with MongoDB

## 1. 地图中遇到的问题

在最初下载上海地区的小样本并运行临时data_explore.py文件后，我注意到了数据的三个主要问题，我将按以下顺序讨论：
- 过分简化的街道名称 如 [Gongji Rd.(E.)]
- 中文路名里面有其他内容 如 [泰安路120弄]
- city名混乱，有些addr:city是"上海",有些是"上海市"，有些是"浦东新区"
- 邮政编码错误，上海没有20开头的右边，如 [314211]

#### 过分简化的街道名称(另外部分英文名称中也包含了街道名称)
我的方案是，对字符传进行处理，将一些简化的字符串还原为正常的。如<br />
Gongji Rd.(E.) ---> Gongji Road(E.)
Bao'an Hwy. ---> Bao'an Highway
另外部分Node和Wat英文名称中也包含了街道名称，这个也要对应地做调整

#### 中文路名里面有其他内容
我的方案是，字符串做判断，发现在"路"后面，只要是数字，就直接截取"路"这个字及以前的部分

#### city名混乱
整个数据集中，有city的不多，所以我打算再导入Mongo的时候，不考虑这个字段，绝大部分都说是"上海"，所以这个字段没有多大意义。

#### 邮政编码错误
我的方案是，判断是不是6位数字，如果不是，直接过滤掉
如果是，再判断前2位是不是20开头的，如果不是，则过滤掉。

### 在此根据以上几点策略，将数据做基本的数据清理后，导入到MongoDB
导入MongoDB的数据格式是：

```javascript
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
          "postcode": "201203",
          "street": "肇家浜路"
          "street:en": "Zhao Jia Bang Road"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "星巴克咖啡",
"name:en"："StarBucks Coffee"
"phone": "1 (773)-271-5176"
}
```

使用以下命令新建mongodb数据库
```
> use openstreetmap
switched to db openstreetmap
```
建立号以后，执行代码 data_wrangling.py 清洗并在mongodb中导入所有的数据

## 2. 数据概述

本节包含有关数据集和用于收集这些数据集的MongoDB查询的基本统计信息。 

OSM文件大小:<br />
ex_shanghai.osm ......... 253 MB<br />
ex_shanghai.osm.json ......... 386 MB<br />

文档数
```shell
> db.arachnid.find().count()
1355351
```

节点(node)和道路(way)的数量
```shell
>  db.arachnid.find({"type":"node"}).count()
1189350
>  db.arachnid.find({"type":"way"}).count()
166001
```

创建数据的用户数(created.user)的数量
```shell
>  db.arachnid.distinct("created.user").length
1649
```

创建数据量最多的前30个用户是:
```shell
> db.arachnid.aggregate(
    [{"$group":{"_id":"$created.user", 
                "count":{"$sum":1}}},
    {"$sort":{"count":-1}}, 
    {"$limit":10}])

{ "_id" : "aighes", "count" : 121454 }
{ "_id" : "zzcolin", "count" : 82635 }
{ "_id" : "xiaotu", "count" : 81101 }
{ "_id" : "Koalberry", "count" : 73348 }
{ "_id" : "Xylem", "count" : 70182 }
{ "_id" : "duxxa", "count" : 67542 }
{ "_id" : "yangfl", "count" : 61903 }
{ "_id" : "alberth2", "count" : 45361 }
{ "_id" : "Austin Zhu", "count" : 44606 }
{ "_id" : "HWST", "count" : 41550 }
```

创建数据量最多的前十个用户创建的数据总共有：
```shell
> db.arachnid.aggregate(
    [{"$group":{"_id":"$created.user", 
                "count":{"$sum":1}}},
    {"$sort":{"count":-1}}, 
    {"$limit":30},
    {"$group":{"_id":null,
               "total":{"$sum":"$count"}}}])

{ "_id" : null, "total" : 997873 }
```


只创建过1条到10条数据的用户有哪些:
```shell
> db.arachnid.aggregate(
    [{"$group":{"_id":"$created.user", 
                "count":{"$sum":1}}},
    {"$group":{"_id":"$count", 
               "num_users":{"$sum":1}}}, 
    {"$sort":{"_id":1}},
    {"$limit":10}])

{ "_id" : 1, "num_users" : 408 }
{ "_id" : 2, "num_users" : 152 }
{ "_id" : 3, "num_users" : 83 }
{ "_id" : 4, "num_users" : 45 }
{ "_id" : 5, "num_users" : 81 }
{ "_id" : 6, "num_users" : 41 }
{ "_id" : 7, "num_users" : 41 }
{ "_id" : 8, "num_users" : 27 }
{ "_id" : 9, "num_users" : 24 }
{ "_id" : 10, "num_users" : 20 }
```

只创建过20条数据一下的用户有哪些:
```shell
> db.arachnid.aggregate(
    [{"$group":{"_id":"$created.user", 
                "count":{"$sum":1}}},
    {"$group":{"_id":"$count", 
               "num_users":{"$sum":1}}}, 
    {"$sort":{"_id":1}},
    {"$limit":10},
    {"$group":{"_id":null,
               "total":{"$sum":"$num_users"}}}])

{ "_id" : null, "total" : 922 }
```

## 3. 其他发现

前10名出现的设施 
```shell
> db.char.aggregate(
    [{"$match":{"amenity":{"$exists":1}}},
    {"$group":{"_id":"$amenity", 
               "count":{"$sum":1}}},
    {"$sort":{"count":1}}, 
    {"$limit":10}])

什么都没有
```

最大的宗教
```shell
> db.char.aggregate(
    [{"$match":{"amenity":{"$exists":1},                                "amenity":"place_of_worship"}}, 
    {"$group":{"_id":"$religion", 
               "count":{"$sum":1}}}, 
    {"$sort":{"count":1}}, 
    {"$limit":1}])

什么都没有
```

最受欢迎的美食 
```shell
> db.char.aggregate(
    [{"$match":{"amenity":{"$exists":1},                                "amenity":"restaurant"}}, 
    {"$group":{"_id":"$cuisine", 
               "count":{"$sum":1}}}, 
    {"$sort":{"count":1}}, 
    {"$limit":2}]) 

什么都没有 
```

## 4. 总结

