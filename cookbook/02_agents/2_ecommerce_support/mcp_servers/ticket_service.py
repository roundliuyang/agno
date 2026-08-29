#!/usr/bin/env python3
"""Ticket Service MCP Server.

Provides ticket creation and management capabilities.
Run with: python mcp_servers/ticket_service.py
"""

from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务，服务名称为 "ticket-service"
# host/port 在构造时设置，run() 时生效
mcp = FastMCP("ticket-service", host="0.0.0.0", port=8002)

# --- 模拟工单存储 ---
# 所有工单都存放在 TICKETS 这个列表里，模拟数据库
TICKETS: list[dict] = []
# 用于生成唯一工单号的计数器，每次创建工单自增
_ticket_counter = 1000


@mcp.tool()
def create_ticket(
    ticket_type: str,
    subject: str,
    description: str,
    customer_email: str,
    priority: str = "P3",
) -> dict:
    """
    创建一个新的支持工单。

    参数说明:
        ticket_type: 工单类型（如 "refund", "plan_change", "bug", "inquiry"）
        subject: 问题简要描述
        description: 详细描述，包括上下文与采取的步骤
        customer_email: 客户的邮箱地址
        priority: 优先级 - P1(最高)、P2(中)、P3(默认)

    返回值:
        包含工单详细信息的字典，包括工单编号。
    """
    global _ticket_counter
    # 每次创建工单时递增工单计数器，确保工单编号唯一
    _ticket_counter += 1
    ticket_id = f"TKT-{_ticket_counter}"

    # 构造工单字典，存储所有字段
    ticket = {
        "ticket_id": ticket_id,  # 工单编号
        "type": ticket_type,  # 工单类型，如退款等
        "subject": subject,  # 简要描述
        "description": description,  # 详细描述
        "customer_email": customer_email,  # 客户邮箱
        "priority": priority,  # 优先级
        "status": "open",  # 工单初始状态为 open
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),  # 创建时间 (UTC 时间戳字符串)
    }
    # 工单添加到全局 TICKETS 列表
    TICKETS.append(ticket)

    # 返回创建成功的信息，包含工单详情和友好信息
    return {
        "success": True,
        "ticket": ticket,
        "message": f"Ticket {ticket_id} created successfully.",
    }


@mcp.tool()
def list_tickets(customer_email: str = "", status: str = "") -> dict:
    """
    列出支持工单，可选条件为客户邮箱和状态过滤。

    参数说明:
        customer_email: 按客户邮箱筛选（默认为空，表示不筛选）
        status: 按工单状态筛选（如 "open", "in_progress", "resolved", "closed"，默认为空不筛选）

    返回值:
        包含匹配工单列表和总数量的字典。
    """
    # 默认返回全部工单
    results = TICKETS
    # 按客户邮箱过滤
    if customer_email:
        results = [t for t in results if t["customer_email"] == customer_email]
    # 按工单状态过滤
    if status:
        results = [t for t in results if t["status"] == status]
    # 返回匹配的工单及总数
    return {"tickets": results, "total": len(results)}


# 升级前：stdio 模式（开发环境，作为 Agent 子进程运行）
# if __name__ == "__main__":
#     mcp.run(transport="stdio")

# 升级后：HTTP 模式（生产环境，作为独立服务运行）
# host/port 已在 FastMCP() 构造时设置
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # 启动后，MCP 端点为：http://localhost:8002/mcp
