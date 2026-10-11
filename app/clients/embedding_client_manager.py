from typing import Optional
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    """嵌入式向量嵌入客户端管理器类 用于管理HuggingFaceEmbeddings客户端的初始化和配置"""

    def __init__(self,config:EmbeddingConfig):
        self.config=config
        self.client:Optional[HuggingFaceEndpointEmbeddings]|None=None


    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        """初始化HuggingFaceEndpointEmbeddings客户端，将拼好的url作为模型地址传入客户端"""

        self.client=HuggingFaceEndpointEmbeddings(model=self._get_url())

#创建向量数据库客户端管理器
embedding_client_manager=EmbeddingClientManager(app_config.embedding)


if __name__ == "__main__":
    # 初始化客户端对象
    embedding_client_manager.init()
    # 对文本进行向量嵌入，返回向量
    result = embedding_client_manager.client.embed_query("hello world")
    # 输出向量和向量长度
    print(result)
    print(len(result))