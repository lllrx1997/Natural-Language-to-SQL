import asyncio
import sys
import uuid
from pathlib import Path

from loguru import logger
from app.conf.app_config import app_config
from app.core.context import get_request_id, set_request_id


#配置日志格式
log_format=(
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "#绿色显示日志时间
    "<level>{level: <8}</level> | "#按级别颜色显示日志级别（左对齐，占8个字符）
    "<magenta>request_id - {extra[request_id]}</magenta> | "  # 品红色显示request_id（从日志extra中获取）
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "# 青色显示日志所在文件、函数、行号
    "<level>{message}</level>"  # 按级别颜色显示日志正文
)


def inject_request_id(record):
    """Loguru 日志补丁函数：为日志记录对象注入request_id(请求唯一标识）保证每条日志都能关联到对应的请求，便于问题排查和请求链路追踪
        Args：
            record：Loguru 的日志记录对象，包含日志的所有上下文信息（如时间、级别、extra等）

    """

    try:
        #尝试从上下文变量中获取当前请求的request_id
        #上下文变量适配异步/多请求场景，可保证不同请求的request_id互不干扰
        request_id=get_request_id()
    except Exception as  e:
        #若获取失败（如上下文变量未初始化、无有效值等异常），生成UUID4作为兜底的唯一标识
        #避免因request_id获取异常导致日志记录异常
        request_id=str(uuid.uuid4())
    #将request_id 存入日志记录的extra字段，供日志格式中{extra[request_id]调用
    record["extra"]["request_id"]=request_id

#移除loguru默认的控制台输出（避免重复输出日志）
logger.remove()

#给日志打补丁，使其在输出每条日志前执行inject_request_id函数，注入request_id
logger=logger.patch(inject_request_id)

#如果配置中开启了控制台日志输出
if app_config.logging.console.enable:
    #添加控制台日志输出器
    logger.add(sink=sys.stdout,level=app_config.logging.console.level,format=log_format)

#如果配置中开启了文件日志输出
if app_config.logging.file.enable:
    #解析日志文件存储路径
    path=Path(app_config.logging.file.path)
    #递归创建日志目录（如果不存在），已存在则不报错
    path.mkdir(parents=True,exist_ok=True)

    #添加文件日志输出器
    logger.add(
        sink=path/"app.log",#日志文件完整路径
        level=app_config.logging.file.level,#文件日志输出级别
        format=log_format,#使用自定义的日志格式
        rotation=app_config.logging.file.rotation,#文件日志轮转条件，也算分割规则吧
        retention=app_config.logging.file.retention,#文件日志保留条件
        encoding="utf-8"#日志文件编码格式
               )
if __name__ == '__main__':

    async def graph(request: str):
        # 获取ID值
        id = get_request_id()
        # 输出结果
        logger.info(id)


    async def req1():
        # 接收到请求
        set_request_id("111111111")
        # 模拟处理
        await asyncio.sleep(1)
        await graph("request-1")


    async def req2():
        # 接收到请求
        set_request_id("2222222222")
        # 模拟处理
        await asyncio.sleep(1)
        await graph("request-2")


    async def main():
        await asyncio.gather(req1(), req2())

    asyncio.run(main())
