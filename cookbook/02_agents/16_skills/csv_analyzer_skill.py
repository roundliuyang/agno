from pathlib import Path
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.skills import LocalSkills, Skills

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# 加载 skills 目录
skills_dir = Path(__file__).parent / "csv-analyzer"

agent = Agent(
    name="Data Analyst",
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
        "你是一个拥有专业技能的数据分析助手。",
        "分析数据时，总是先运行分析脚本，再解读结果。",
    ],
    markdown=True,
)

if __name__ == "__main__":
    csv_path = str(Path(__file__).parent / "data" / "sales_2024.csv")
    agent.print_response(
        f"请分析 {csv_path} 文件，给我一份关键发现的摘要。"
    )
