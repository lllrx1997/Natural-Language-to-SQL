import asyncio
from typing import Optional
from elasticsearch import AsyncElasticsearch
from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    """ES异步客户端管理器：封装ES客户端的初始化、链接、关闭逻辑"""


    def __init__(self,config:ESConfig):
        self.config=config,
        self.client:Optional[AsyncElasticsearch]|None=None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client=AsyncElasticsearch(
            hosts=[self._get_url()]
        )

    async def close(self):
        await self.client.close()
#创建ES客户端管理器对象

es_client_manager=ESClientManager(app_config.es)

if __name__ == "__main__":
    async def test():
        es_client_manager.init()
        client = es_client_manager.client
        index_name = "my_index"
        # 创建索引
        if await client.indices.exists(index=index_name):
            await client.indices.delete(index=index_name)
        result = await client.indices.create(
            index=index_name,
            mappings={
                "dynamic": False,
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            },
        )
        # print(result)
        """
        result为
        {'acknowledged': True, 'shards_acknowledged': True, 'index': 'my_book_index'}
        请求到达 → acknowledged（集群接收）
         → 分片分配 → shards_acknowledged（索引可用）
                     → index（哪个索引）
        """

        # 批量插入数据
        result = await client.bulk(
            operations=[
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
            # refresh=True # 自动刷新保存
        )
        print(result)
        '''
        没有自动刷新的result
            {
              "errors": false, # 没有错误
              "took": 0, # 耗时 0ms（数据量小，几乎瞬间完成）
              "items": [ # 写入的数据记录
                {
                  "index": { 
                    "_index": "my_book_index", #写入的目标索引
                    "_id": "VzhP4p4BmoQ6EZpiUVHq", #文档 ID
                    "_version": 1, #第 1 版（新文档）
                    "result": "created", #创建成功（vs "updated"）
                    "_shards": { #分片情况
                      "total": 2, #1 个主分片 + 1 个副本 = 2
                      "successful": 1, #主分片确认写入（副本异步跟上）
                      "failed": 0 #无失败
                    },
                    "_seq_no": 0, #分片级别的序列号（第 0 条写入）
                    "_primary_term": 1, #主分片任期号
                    "status": 201 #HTTP 201 Created
                  }
                },
                ...
              ]
            }
            - 有自动刷新的result
                {
                  "index": {
                    "_index": "my_book_index",
                    "_id": "XDhY4p4BmoQ6EZpiNVEf",
                    "_version": 1,
                    "result": "created",
                    "forced_refresh": true, # 自动刷新保存
                    "_shards": {
                      "total": 2,
                      "successful": 1,
                      "failed": 0
                    },
                    "_seq_no": 0,
                    "_primary_term": 1,
                    "status": 201
                  }
                },
        '''
        # 刷新保存索引数据
        await client.indices.refresh(index=index_name)

        # 全文搜索
        result = await client.search(
            index=index_name,
            query={ # 搜索条件
                "match": { # 匹配字段
                    "name": "Brave New World" # 匹配字段名称和值
                }
            },
        )
        print(result)

        # 关闭ES客户端
        await es_client_manager.close()

    asyncio.run(test())

    '''
    搜索的result结构
    - 未命中
        {
          "took": 1,  #耗时2s
          "timed_out": false,  #未超时 默认超时时间是30s
          "_shards": { # 目标索引分片情况
            "total": 1, # 一个分片
            "successful": 1, # 一个分片成功返回
            "skipped": 0,  # 没有分片被跳过，都扫描了
            "failed": 0 # 0 个分片执行失败
          },
          "hits": {  # 命中结果
            "total": {
              "value": 0, # 没有任何一条文档匹配你的查询条件
              "relation": "eq"
            },
            "max_score": null, # 最高相关性评分，没有命中时为null
            "hits": [] # 命中的文档数组，没有命中为[]
          }
        }
    - 有命中
        {
          "took": 1,  #耗时1s
          "timed_out": false,  #未超时 默认超时时间是30s
          "_shards": { # 目标索引分片情况
            "total": 1, # 一个分片
            "successful": 1, # 一个分片成功返回
            "skipped": 0,  # 没有分片被跳过，都扫描了
            "failed": 0 # 0 个分片执行失败
          },
          "hits": { # 命中结果
            "total": { # 总的情况
              "value": 1, # 命中 1 条文档
              "relation": "eq" # 精确计数（非估算下界）
            },
            "max_score": 1.2067741, # 最高 BM25 相关性评分
            "hits": [ # 命中的文档列表
              {
                "_index": "my_index2", # 所属索引名称
                "_id": "TDg34p4BmoQ6EZpi9lEq", # 文档id
                "_score": 1.2067741, # 该文档的相关度评分
                "_source": { # 原始文档
                  "name": "The Handmaids Tale",
                  "author": "Margaret Atwood",
                  "release_date": "1985-06-01",
                  "page_count": 311
                }
              }
            ]
          }
        }
    '''

