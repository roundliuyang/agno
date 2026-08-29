from pathlib import Path
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.skills import LocalSkills, Skills

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# 加载 skills 目录
skills_dir = Path(__file__).parent / "writing-assistant"

agent = Agent(
    name="Writing Assistant",
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
    skills=Skills(loaders=[LocalSkills(str(skills_dir))]),
    instructions=[
        "你是一个拥有专业技能的写作助手。",
        "在起草文档前，总是要先加载相关的参考模板。",
    ],
    markdown=True,
)

if __name__ == "__main__":
    agent.print_response(
        "帮我写一封项目进展邮件发送给我的团队。我们本周完成了用户认证模块，下周计划开始支付集成。"
    )
