from pathlib import Path
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.skills import Skills, LocalSkills

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# 加载 skills 目录
skills_dir = Path(__file__).parent / "hello-world"

agent = Agent(
    name="Greeting Agent",
    model=OpenAIChat(
        id=os.getenv("SILICONFLOW_CHAT_MODEL"),
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url=os.getenv("SILICONFLOW_BASE_URL"),
        role_map={"system": "system", "user": "user", "assistant": "assistant", "tool": "tool", "model": "assistant"},
    ),
    skills=Skills(loaders=[LocalSkills(str(skills_dir))]),
    instructions=["你是一个可以访问专业技能的乐于助人的助手。"],
    markdown=True,
)

# 运行 Agent
agent.print_response("请欢迎我们的新团队成员Tommy，他刚刚加入工程团队。")
