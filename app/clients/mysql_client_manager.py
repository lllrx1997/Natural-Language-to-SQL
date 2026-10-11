"""
操作mysql数据库数据的客户端管理器模块
"""
import asyncio
from typing import Optional
from sqlalchemy import text, Select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from app.conf.app_config import app_config
from app.conf.app_config import DBConfig
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MysqlClientManager:
    def __init__(self,config:DBConfig):
        self.config = config
        self.engine:Optional[AsyncEngine]=None
        self.session_factory: Optional[async_sessionmaker] = None
    #获取链接的url
    def _get_url(self):
        return (
            f"mysql+asyncmy://{self.config.user}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}"
            f"/{self.config.database}?charset=utf8mb4"
        )
    #初始化
    def init(self):
        #创建一个异步引擎
        self.engine=create_async_engine(
            self._get_url(),
            pool_size=10,#内部连接池中缓存的长久连接数，默认是5
            pool_pre_ping=True,# 是否开启自动检测连接是否可用的开关，true代表开启检测，防止连接意外被关闭导致失败 默认是False
        )

        #创建一个异步会话工厂
        self.session_factory=async_sessionmaker(self.engine, expire_on_commit=False,autoflush=False,autobegin=True)

        #释放资源
    async def close(self):
        await self.engine.dispose()

    #创建操作dw库的客户端管理器
dwMysqlClientManager=MysqlClientManager(app_config.db_dw)
#创建操作meta的客户端管理器
metaMysqlClientManager=MysqlClientManager(app_config.db_meta)

if __name__ == "__main__":
    # 测试ORM的更新和删除
    async def test_orm2():
        # 初始化meta客户端对象
        metaMysqlClientManager.init()

        # 创建异步会话
        async with metaMysqlClientManager.session_factory() as session:
            session: AsyncSession

            # 查询一条数据
            table_info = await session.get(TableInfoMySQL, "dim_customer1")
            print(table_info.description)

            # 添加一条数据
            # table_info.description = "xxxx"

            # 删除一条数据
            await session.delete(table_info)

            # 提交事务
            await session.commit()

        # 释放资源
        await metaMysqlClientManager.close()


    # 测试orm的添加和查询
    async def test_orm():
        # 初始化meta客户端对象
        metaMysqlClientManager.init()

        # 创建异步会话
        async with metaMysqlClientManager.session_factory() as session:
            session: AsyncSession
            # 添加一条数据
            info1 = TableInfoMySQL(
                id="dim_customer1",
                name="dim_customer1",
                role="dim",
                description="客户信息维度表1"
            )
            session.add(info1)
            # 再添加一条数据
            info2 = TableInfoMySQL(
                id="dim_customer2",
                name="dim_customer2",
                role="dim",
                description="客户信息维度表2"
            )
            session.add(info2)

            # 提交事务
            await session.commit()

            # 查询一条数据
            table_info = await session.get(TableInfoMySQL, "dim_customer1")
            print(table_info.description)

            # 查询多条数据
            # result = await session.execute(Select(TableInfoMySQL).limit(2))
            result = await session.execute(
                Select(TableInfoMySQL).from_statement(text("select * from table_info limit 2")))
            rows: list[TableInfoMySQL] = result.scalars().all()
            print(rows)
            print(rows[0].description)

            # 看是否可以在提交事务后读取ORM对象的属性
            # print(info1.name)

        # 释放资源
        await metaMysqlClientManager.close()


    asyncio.run(test_orm())