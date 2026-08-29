#!/usr/bin/env python3
"""
源码详解

本脚本用于模拟检查电商服务系统中各个子服务的健康状态，便于自动化故障排查协作。

用法:
    ./check_service_status.py [service_name]

参数:
    service_name (可选): 指定要检查的服务名称，缺省为"all"（全部服务）。
    可选值: auth, api, storage, sync

输出:
    以JSON格式输出服务状态信息，包括检查时间、各服务的详细状态、整体健康状态。

主要逻辑说明:
    1. 定义若干模拟服务及其健康状态数据
    2. 根据传入参数决定返回全部结果还是单个服务详情
    3. 汇总整体健康状况
    4. 主入口以JSON方式打印结果，异常时输出错误信息
"""

import json
import sys
from datetime import datetime, timezone


def check_status(service: str = "all") -> dict:
    """
    模拟检查服务健康状态。
    实际生产环境应调用HTTP健康检查端点。

    参数:
        service: 服务名，默认"all"（全部服务）

    返回:
        dict，包含检查时间、服务详情、整体状态（operational/degraded）
    """
    open("debug.log", "a").write(f"--------------------{service}--------------------\n")
    # 构造模拟服务状态数据
    services = {
        "auth": {
            "name": "Authentication Service",
            "status": "operational",
            "response_time_ms": 45,
            "uptime_percent": 99.98,
        },
        "api": {
            "name": "Core API",
            "status": "operational",
            "response_time_ms": 120,
            "uptime_percent": 99.95,
        },
        "storage": {
            "name": "Storage Service",
            "status": "degraded",
            "response_time_ms": 850,
            "uptime_percent": 99.80,
            "incident": "Elevated latency in US-East region",
        },
        "sync": {
            "name": "Sync Service",
            "status": "operational",
            "response_time_ms": 200,
            "uptime_percent": 99.92,
        },
    }

    # 返回单个服务或全部服务的状态
    if service != "all" and service in services:
        result = {service: services[service]}
    else:
        result = services

    # 汇总overall状态：只要有一个非operational服务则视为degraded
    overall_status = (
        "degraded"
        if any(s["status"] != "operational" for s in result.values())
        else "operational"
    )

    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "services": result,
        "overall_status": overall_status,
    }


if __name__ == "__main__":
    try:
        service_name = sys.argv[1] if len(sys.argv) > 1 else "all"
        result = check_status(service_name)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
