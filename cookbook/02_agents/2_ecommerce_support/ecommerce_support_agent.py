"""E-commerce Customer Support Agent —— 结合 Skills 与 MCP 系统。

Skills（技能）为代理提供领域知识（如公司政策、产品信息、操作指南）。
MCP 工具用于与外部业务系统交互（如订单查询、工单创建等）。

前置条件（HTTP 模式）：
    先在独立终端中启动 MCP Server：
        python cookbook/02_agents/2_ecommerce_support/mcp_servers/order_service.py   # → :8001
        python cookbook/02_agents/2_ecommerce_support/mcp_servers/ticket_service.py  # → :8002

用法：
    # 交互式选择场景
    python cookbook/02_agents/2_ecommerce_support/ecommerce_support_agent.py

    # 运行指定场景（1/2/3，逗号分隔可多选）
    python cookbook/02_agents/2_ecommerce_support/ecommerce_support_agent.py --scenario 1
    python cookbook/02_agents/2_ecommerce_support/ecommerce_support_agent.py --scenario 1,3
    python cookbook/02_agents/2_ecommerce_support/ecommerce_support_agent.py --scenario all
"""

import argparse
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.skills import LocalSkills, Skills
from agno.tools.mcp import MCPTools

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# 路径以本脚本为基准
SCRIPT_DIR = Path(__file__).parent
SKILLS_DIR = SCRIPT_DIR / "skills"

# MCP Server HTTP 端点（需要先独立启动 MCP Server）
ORDER_MCP_URL = os.getenv("ORDER_MCP_URL", "http://localhost:8001/mcp")
TICKET_MCP_URL = os.getenv("TICKET_MCP_URL", "http://localhost:8002/mcp")

# ── 场景定义 ─────────────────────────────────────────────────
SCENARIOS = {
    "1": {
        "title": "退款请求（Skill + MCP 协同）",
        "prompt": (
            "你好，我想申请订单 ORD-2024-1001 的退款。"
            "我五天前购买了年度Pro套餐，但该产品并不适合我们团队的需求。"
            "我的邮箱是 alice@example.com。"
        ),
    },
    "2": {
        "title": "产品咨询（仅用 Skill）",
        "prompt": (
            "Pro 套餐和 Enterprise 套餐有什么区别？"
            "我需要为25人的团队使用 SSO。"
        ),
    },
    "3": {
        "title": "跨领域 - 故障排查 + 订单查询（Skill + MCP 跨域协作）",
        "prompt": (
            "我的文件无法同步，我担心超出了存储额度。"
            "我的订单号是 ORD-2024-1002，能帮我查一下吗？"
        ),
    },
}


def select_scenarios_interactive() -> list[str]:
    """交互式菜单，让用户选择要运行的场景。"""
    print("\n可用场景：")
    print("-" * 50)
    for key, scenario in SCENARIOS.items():
        print(f"  [{key}] {scenario['title']}")
    print("  [a] 运行全部场景")
    print("-" * 50)

    choice = input("请选择场景编号（多选用逗号分隔，如 1,3）: ").strip().lower()

    if choice in ("a", "all"):
        return list(SCENARIOS.keys())

    selected = [s.strip() for s in choice.split(",") if s.strip() in SCENARIOS]
    if not selected:
        print("未选择有效场景，默认运行全部。")
        return list(SCENARIOS.keys())

    return selected


def parse_args() -> list[str] | None:
    """解析命令行参数，返回场景列表或 None（进入交互模式）。"""
    parser = argparse.ArgumentParser(description="E-commerce Support Agent")
    parser.add_argument(
        "--scenario", "-s",
        type=str,
        default=None,
        help='要运行的场景编号，逗号分隔（如 "1,3"）或 "all" 运行全部',
    )
    args = parser.parse_args()

    if args.scenario is None:
        return None

    if args.scenario.lower() == "all":
        return list(SCENARIOS.keys())

    selected = [s.strip() for s in args.scenario.split(",") if s.strip() in SCENARIOS]
    if not selected:
        parser.error(f"无效的场景编号: {args.scenario}（可选: {', '.join(SCENARIOS.keys())}, all）")

    return selected


def create_agent(order_mcp: MCPTools, ticket_mcp: MCPTools) -> Agent:
    """创建配置了 Skills + MCP 的客服 Agent。"""
    return Agent(
        name="电商客服支持代理",
        model=OpenAIChat(
            id=os.getenv("SILICONFLOW_CHAT_MODEL"),
            api_key=os.getenv("SILICONFLOW_API_KEY"),
            base_url=os.getenv("SILICONFLOW_BASE_URL"),
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        # 技能：利用本地知识库为代理提供产品政策、比较、故障排查等
        skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
        # MCP 工具：用于订单查询、工单创建等
        tools=[order_mcp, ticket_mcp],
        instructions=[
            "你是一名专业的电商客户支持代理。",
            "",
            "## 如何使用你的能力",
            "",
            "你拥有两类主要能力：",
            "1. 技能（知识）：通过 get_skill_* 工具加载退款政策、产品指南、排障流程等知识内容。",
            "2. MCP 工具（操作）：可用于查询订单、处理退款和创建工单。",
            "",
            "## 决策流程",
            "",
            "针对每个客户请求，请遵循以下流程：",
            "1. 理解：优先加载相关技能，理解相关政策和流程。",
            "2. 调查：通过 MCP 工具查询客户的实际业务数据。",
            "3. 决策：结合政策，针对客户情况给出建议。",
            "4. 行动：如有必要，使用 MCP 工具执行实际操作。",
            "5. 记录：涉及退款或套餐变更需创建工单记录。",
            "",
            "## 技能选择指南",
            "",
            "- 产品/功能/价格类问题：选择 product-faq 技能",
            "- 错误/故障/性能问题：选择 troubleshoot 技能",
            "- 账单/退款/套餐变更：选择 order-helper 技能",
            "- 若涉及多个领域，可同时加载多个技能。",
            "",
            "## 重要规则",
            "",
            "- 在通过 MCP 工具操作前，务必优先加载相关技能。",
            "- 处理退款前，必须先参考退款政策。",
            "- 所有退款及套餐变更操作都需创建工单记录。",
            "- 保持共情、透明，专注于解决客户问题。",
            "- 回应需使用客户的语言。",
        ],
        markdown=True,
    )


async def run_scenario(agent: Agent, scenario_id: str) -> None:
    """运行单个场景。"""
    scenario = SCENARIOS[scenario_id]
    print("\n" + "=" * 60)
    print(f"场景{scenario_id}：{scenario['title']}")
    print("=" * 60)
    await agent.aprint_response(scenario["prompt"])


async def main():
    # 解析场景选择
    selected = parse_args()
    if selected is None:
        selected = select_scenarios_interactive()

    # --- MCP 工具：通过 HTTP 连接独立运行的 MCP Server ---
    order_mcp = MCPTools(
        url=ORDER_MCP_URL,
        transport="streamable-http",
    )
    ticket_mcp = MCPTools(
        url=TICKET_MCP_URL,
        transport="streamable-http",
    )

    agent = create_agent(order_mcp, ticket_mcp)

    # 按顺序运行所选场景
    for scenario_id in selected:
        await run_scenario(agent, scenario_id)


if __name__ == "__main__":
    asyncio.run(main())
