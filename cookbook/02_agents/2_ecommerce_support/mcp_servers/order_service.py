#!/usr/bin/env python3
"""Order Service MCP Server.

Provides order query, payment check, and refund processing capabilities.
Run with: python mcp_servers/order_service.py
"""

from datetime import datetime, timedelta, timezone

from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 实例，服务名为 "order-service"
# host/port 在构造时设置，run() 时生效
mcp = FastMCP("order-service", host="0.0.0.0", port=8001)

# --- 模拟订单数据库 ---
# 使用内存中的字典模拟简单的订单数据库，Key 为订单号，Value 为订单详情
ORDERS_DB = {
    "ORD-2024-1001": {
        "order_id": "ORD-2024-1001",
        "customer_email": "alice@example.com",
        "customer_name": "Alice Wang",
        "plan": "Pro",  # 订购套餐类型
        "billing_cycle": "annual",  # 计费周期
        "amount": 288.00,  # 金额
        "currency": "USD",  # 货币类型
        "status": "active",  # 当前订单状态
        "created_at": (
            datetime.now(timezone.utc) - timedelta(days=5)
        ).isoformat(),  # 下单时间（距今5天）
        "payment_method": "credit_card",  # 支付方式
        "is_first_purchase": True,  # 是否为首次购买
    },
    "ORD-2024-1002": {
        "order_id": "ORD-2024-1002",
        "customer_email": "bob@example.com",
        "customer_name": "Bob Li",
        "plan": "Pro",
        "billing_cycle": "monthly",
        "amount": 29.00,
        "currency": "USD",
        "status": "active",
        "created_at": (
            datetime.now(timezone.utc) - timedelta(days=45)
        ).isoformat(),  # 距今45天
        "payment_method": "credit_card",
        "is_first_purchase": False,
    },
    "ORD-2024-1003": {
        "order_id": "ORD-2024-1003",
        "customer_email": "charlie@example.com",
        "customer_name": "Charlie Zhang",
        "plan": "Enterprise",
        "billing_cycle": "annual",
        "amount": 5000.00,
        "currency": "USD",
        "status": "active",
        "created_at": (
            datetime.now(timezone.utc) - timedelta(days=120)
        ).isoformat(),  # 距今120天
        "payment_method": "bank_transfer",
        "is_first_purchase": False,
    },
}


@mcp.tool()
def query_order(order_id: str = "", customer_email: str = "") -> dict:
    """通过订单号或邮箱查询订单详情。

    Args:
        order_id: 订单号 (如 "ORD-2024-1001")，可选
        customer_email: 客户邮箱，查找所有关联订单，可选

    Returns:
        命中时返回订单详细信息，否则返回未找到提示。
    """
    # 先按订单号精确查询
    if order_id and order_id in ORDERS_DB:
        return {"found": True, "order": ORDERS_DB[order_id]}

    # 若按邮箱查询，则查找所有匹配该邮箱的订单
    if customer_email:
        matches = [
            o for o in ORDERS_DB.values() if o["customer_email"] == customer_email
        ]
        if matches:
            return {"found": True, "orders": matches}

    # 未找到匹配的订单时
    return {"found": False, "message": "No order found with the given criteria."}


@mcp.tool()
def check_payment(order_id: str) -> dict:
    """检查指定订单的付款状态。

    Args:
        order_id: 需要查询的订单号

    Returns:
        返回付款方式、金额、币种及最近扣费时间等信息。
    """
    # 如果订单号不存在于模拟数据库，则报错
    if order_id not in ORDERS_DB:
        return {"error": f"Order {order_id} not found."}

    order = ORDERS_DB[order_id]
    # 假设所有订单均为已付款状态
    return {
        "order_id": order_id,
        "payment_method": order["payment_method"],
        "amount": order["amount"],
        "currency": order["currency"],
        "status": "paid",
        "last_charge_date": order["created_at"],
    }


@mcp.tool()
def process_refund(order_id: str, reason: str, refund_type: str = "full") -> dict:
    """处理订单退款请求。

    Args:
        order_id: 退款订单号
        reason: 退款原因（必填，对账用途）
        refund_type: 退款类型："full" 全额，"prorated" 部分退款，默认为全额

    Returns:
        退款确认，包括金额、预计到账时间等信息（模拟数据）
    """
    # 若订单号不存在，返回失败
    if order_id not in ORDERS_DB:
        return {"success": False, "error": f"Order {order_id} not found."}

    order = ORDERS_DB[order_id]
    # 简单按类型决定退款金额：全额则等于原单金额，部分（prorated）则一半
    refund_amount = order["amount"] if refund_type == "full" else order["amount"] * 0.5

    return {
        "success": True,
        "refund_id": f"REF-{order_id}",  # 模拟退款编号
        "order_id": order_id,
        "refund_amount": refund_amount,
        "currency": order["currency"],
        "refund_type": refund_type,
        "reason": reason,
        "estimated_processing_days": 7,  # 固定7天模拟到账周期
        "refund_to": order["payment_method"],  # 退款至原支付方式
    }


# 升级前：stdio 模式（开发环境，作为 Agent 子进程运行）
# if __name__ == "__main__":
#     mcp.run(transport="stdio")

# 升级后：HTTP 模式（生产环境，作为独立服务运行）
# host/port 已在 FastMCP() 构造时设置
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # 启动后，MCP 端点为：http://localhost:8001/mcp
