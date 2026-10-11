import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.clients.mysql_client_manager import dw_mysql_client_manager


class DWMysqlRepository:
    """操作dw数据库的持久类"""

    def __init__(self,session:AsyncSession):
        self.session=session


    async def get_column_values(self,table_name:str,column_name:str,limit:int=10):

        """
        查询指定字段的取值
        :param table_name:
        :param column_name:
        :param limit:
        :return: ["C001","C002","C003"]
        """

        #定义sql
        sql=f"select distinct {column_name} from {table_name} limit {limit}"
        #执行sql
        result=await self.session.execute(text(sql))

        #[row(),row(),row()]

        #获取结果，组装数据
        return {row.Field:row.Type for row in result.all()}


if __name__ == '__main__':

    async def test1():
        dw_mysql_client_manager.init()
        async with dw_mysql_client_manager.session_factory() as session:
            rep = DWMysqlRepository(session)
            result = await rep.get_column_values("dim_customer", "customer_name")
            print(result)
        await dw_mysql_client_manager.close()

    async def test2():
        dw_mysql_client_manager.init()
        async with dw_mysql_client_manager.session_factory() as session:
            rep = DWMysqlRepository(session)
            result = await rep.get_column_types("dim_customer")
            print(result)
        await dw_mysql_client_manager.close()

    asyncio.run(test1())
    asyncio.run(test2())
