import asyncio
from csv import excel

from sqlalchemy import column, except_

from app.conf.meta_config import meta_config
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.core.log import logger
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build():
    #初始化各个客户端管理器
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    qdrant_client_manager.init()
    embedding_client_manager()
    es_client_manager.init()

    try:
        #创建session对象
        async with (meta_mysql_client_manager.session_factory() as meta_session,dw_mysql_client_manager.session_fatory() as dw_session):
            #创建持久层对象
            meta_mysql_repository=MetaMysqlRepository(meta_session)
            dw_mysql_repository=DWMysqlRepository(dw_session)
            column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client)
            value_es_repository=ValueESRepository(es_client_manager.client)
            metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client)

            meta_knowledge_service=MetaKnowledgeService(
                meta_mysql_repo=meta_mysql_repository,
                dw_mysql_repo=dw_mysql_repository,
                column_qdrant_repo=column_qdrant_repository,
                value_es_repo=value_es_repository,
                metric_qdrant_repo=metric_qdrant_repository,
                embedding_client=embedding_client_manager.client,
            )
            #启动构建原数据知识库的业务流程
            await meta_knowledge_service.build(meta_config)
            except Exception as e:

            logger.error(f"构建元数据知识库出错：{str(e)}")
            raise e

    finally:
        #关闭客户端管理器
        await meta_mysql_client_manager.close()
        await dw_mysql_client_manager.close()
        await qdrant_client_manager.close()
        await es_client_manager.close()

if __name__ == "__main__":
    asyncio.run(build())


