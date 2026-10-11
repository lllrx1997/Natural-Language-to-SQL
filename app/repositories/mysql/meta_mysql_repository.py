


from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL



class MetaMysqlRepository:
    """操作meta库的持久层类"""
    def __init__(self,session:AsyncSession):
        self.session=session

    async def save_table_infos(self,table_infos:list[TableInfoMySQL]):
        """向table_info表中插入多条数据"""
        self.session.add_all(table_infos)

    async def save_column_infos(self,column_infos:list[ColumnInfoMySQL]):
        """向column_info表中插入多条数据"""
        self.session.add_all(column_infos)


    async def save_metric_info(self,metric_infos:list[MetricInfoMySQL]):
        """向metric_info表中插入多条数据"""
        self.session.add_all(metric_infos)

    async def save_column_column_metric_infos(self,column_metric_infos:list[ColumnMetricMySQL]):
        """向column_metric表中插入多条数据"""
        self.session.add_all(column_metric_infos)

    async def get_column_info_by_id(self,id:str)->ColumnInfoMySQL:
        """根据字段id查询列对象信息"""

        return await self.session.get(ColumnInfoMySQL,id)

    async def get_column_infos_by_table_id (self,table_id:str)->list[ColumnInfoMySQL]:
        """根据表id，查询表的主外键字段"""
        sql="""
            select * from_info where table_id=:table_id and role in ('primary_key','foreign_key')        
        """
        query =select(ColumnInfoMySQL).from_statement(text(sql))
        result=await self.session.execute(query,{"table_id":table_id})
        return result.scalars().all()


    async def get_table_info_by_id(self,table_id:str)->TableInfoMySQL:
        """根据表id查询表信息TableInfoMysql"""
        return await self.session.get(TableInfoMySQL,table_id)

















