import asyncio
from contextvars import ContextVar

"""创建上下文变量对象，用于异步/多请求场景下存储和获取当前请求的唯一标识request_id
    参数1：上下文变量的名称，用于标识变量的用途
    参数2：指定默认值，当未显示设置request_id时，获取到的值为1
"""

_req_id_context_var:ContextVar[int]=ContextVar("request_id",default=1)

def set_request_id(request_id:int):
    """保存request_id"""

    _req_id_context_var.set(request_id)

def get_request_id()->int:
    """读取保存的request_id"""

    return _req_id_context_var.get()
if __name__ == "__main__":

    # 测试同一个请求中操作
    async def test1():
        print("====在同一个请求中（也就是同一个循环任务中操作）===）")
        print(f"获取request_id={get_request_id()}")
        set_request_id(3)
        print(f"设置为3后获取reqeust_id={get_request_id()}")
        set_request_id(4)
        print(f"设置为4后获取reqeust_id={get_request_id()}")

    asyncio.run(test1())

    # 模拟请求1操作
    async def req1():
        print("执行请求1..。")
        print(f"获取request_id={get_request_id()}")
        set_request_id(5)
        print(f"设置为5后获取reqeust_id={get_request_id()}")

    # 模拟请求2操作
    async def req2():
        print("执行请求2..。")
        print(f"获取request_id={get_request_id()}")
        set_request_id(6)
        print(f"设置为6后获取reqeust_id={get_request_id()}")

    # 测试不同请求中操作
    async def test2():
        print("====在多个请求中（也就是多个循环任务中操作===")
        cor1 = req1()
        cor2 = req2()
        await asyncio.gather(cor1, cor2)

    asyncio.run(test2())
