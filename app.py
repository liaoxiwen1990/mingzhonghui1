import os
import streamlit as st
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== 配置 ====================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "566deedb4e5f416a9b9b4a943c6145e2.LlT9DuYr53VhSAUr")
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "glm-4.7")

# 页面配置
st.set_page_config(
    page_title="English Tutor",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    /* 页面整体样式 */
    .main-content {
        padding-top: 1rem;
    }
    /* 聊天消息样式 */
    [data-testid="stChatMessageContent"] {
        padding: 0.5rem 1rem;
    }
    /* 侧边栏按钮样式 */
    .stButton button {
        width: 100%;
    }
    /* 聊天消息容器居中 */
    .main {
        padding-top: 2rem !important;
        padding-bottom: 350px !important;
    }
    /* 底部激励语 - 固定位置 */
    .footer-fixed {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        text-align: center;
        padding: 0.5rem;
        background-color: #f8f9fa;
        color: #666;
        font-size: 0.85rem;
        border-top: 1px solid #e0e0e0;
        z-index: 9999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    .footer-text {
        margin: 0.3rem 0;
    }
    /* 为底部激励语留出空间 */
    .main .block-container {
        padding-bottom: 350px !important;
    }
    /* 确保聊天消息不被遮挡 */
    [data-testid="stChatMessageContent"] {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 标题和副标题
st.title("📚 English Tutor")
st.markdown("**你的英语学习助手**")
st.markdown("---")

# 系统提示词
SYSTEM_PROMPT = """You are a friendly and patient English Tutor. Your goal is to help learners improve their English skills.

Guidelines:
- Explain concepts clearly and simply
- Provide examples to illustrate grammar points
- Correct mistakes gently with explanations
- Offer alternatives for better expressions
- Be encouraging and supportive
- Answer in the same language as the question (English or Chinese)
- For English responses, keep them appropriate for the learner's level

Focus on being helpful, clear, and encouraging!"""

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """**Welcome!** 👋

我是你的英语学习助手，可以帮助你：

• 📝 语法问题解答
• 📚 词汇详细解释
• ✍️ 写作改进建议
• 🗣️ 口语练习指导
• 🎧 听力技巧分享

**Feel free to ask me anything in English or Chinese!**

你可以用中文或英文向我提问。"""
        }
    ]

# ==================== 调用 Anthropic Claude API ====================
def call_claude_api(messages):
    try:
        # 将 messages 转换为 Claude 格式
        system_prompt = ""
        claude_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                claude_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                claude_messages.append({"role": "assistant", "content": msg["content"]})

        payload = {
            "model": ANTHROPIC_MODEL,
            "messages": claude_messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        response = requests.post(f"{ANTHROPIC_BASE_URL}/v1/messages", json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()

        if "content" in result and len(result["content"]) > 0:
            return result["content"][0]["text"]
        else:
            return "抱歉，AI返回的格式有误，请稍后重试。"

    except requests.exceptions.Timeout:
        return "请求超时，请检查网络连接后重试。"
    except requests.exceptions.ConnectionError:
        return "网络连接失败，请检查您的网络设置。"
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return "API密钥无效，请检查配置。"
        elif response.status_code == 429:
            return "请求过于频繁，请稍后再试。"
        else:
            return f"API请求失败 (HTTP {response.status_code}): {str(e)}"
    except Exception as e:
        return f"发生未知错误: {str(e)}"

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("Type your question... 输入你的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI回复
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(st.session_state.messages)
            ai_reply = call_claude_api(messages)
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")

    # 清除对话
    st.markdown("### 🗑️ 清除对话")
    if st.button("新建对话", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """**Welcome!** 👋

我是你的英语学习助手，可以帮助你：

• 📝 语法问题解答
• 📚 词汇详细解释
• ✍️ 写作改进建议
• 🗣️ 口语练习指导
• 🎧 听力技巧分享

**Feel free to ask me anything in English or Chinese!**

你可以用中文或英文向我提问。"""
            }
        ]
        st.rerun()

    st.markdown("---")

    # 快捷问题
    st.markdown("### ⚡ 快捷问题")
    quick_prompts = [
        "Explain past tense / 解释过去时",
        "How to use 'the' vs 'a' / 冠词用法",
        "Correct my English / 帮我改错",
        "Vocabulary for daily life / 日常词汇",
        "Tips for speaking fluently / 流利口语技巧"
    ]
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True, key=f"quick_{prompt}"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(st.session_state.messages)
            # 获取模型回复
            with st.spinner("Thinking..."):
                ai_reply = call_claude_api(messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.rerun()

    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.info("""
    - 支持中英文提问
    - 点击快捷问题快速开始
    - 随时新建对话重新开始
    """)

# 底部激励语 - 固定在页面底部
st.markdown(
    """
    <div class="footer-fixed">
        <div class="footer-text" style="color: #888;">Designed by Mingzhonghui，</div>
    </div>
    """,
    unsafe_allow_html=True
)
