import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>챗미나이</title>

<style>
body {
    margin: 0;
    background: #f5f5f5;
    font-family: Arial, sans-serif;
}

.header {
    background: #111;
    color: white;
    padding: 18px;
    font-size: 22px;
    font-weight: bold;
}

#chat {
    height: calc(100vh - 140px);
    overflow-y: auto;
    padding: 20px;
}

.message {
    margin: 12px 0;
    padding: 12px 16px;
    border-radius: 15px;
    max-width: 75%;
    line-height: 1.5;
    white-space: pre-wrap;
}

.user {
    background: #222;
    color: white;
    margin-left: auto;
}

.ai {
    background: white;
    color: #222;
    margin-right: auto;
}

.input-area {
    position: fixed;
    bottom: 0;
    width: 100%;
    display: flex;
    padding: 12px;
    box-sizing: border-box;
    background: white;
}

input {
    flex: 1;
    padding: 14px;
    border: 1px solid #ccc;
    border-radius: 12px;
    font-size: 16px;
}

button {
    margin-left: 8px;
    padding: 14px 20px;
    border: none;
    border-radius: 12px;
    background: #111;
    color: white;
    cursor: pointer;
}
</style>
</head>

<body>

<div class="header">
    🤖 챗미나이
</div>

<div id="chat">
    <div class="message ai">
        안녕하세요! 저는 챗미나이입니다. 무엇을 도와드릴까요?
    </div>
</div>

<div class="input-area">
    <input
        id="input"
        placeholder="메시지를 입력하세요..."
        onkeydown="if(event.key==='Enter') sendMessage()"
    >
    <button onclick="sendMessage()">전송</button>
</div>

<script>

async function sendMessage() {

    const input = document.getElementById("input");
    const chat = document.getElementById("chat");

    const message = input.value.trim();

    if (!message) return;

    chat.innerHTML += `
        <div class="message user">
            ${escapeHtml(message)}
        </div>
    `;

    input.value = "";

    const loading = document.createElement("div");
    loading.className = "message ai";
    loading.textContent = "생각 중...";
    chat.appendChild(loading);

    chat.scrollTop = chat.scrollHeight;

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        loading.textContent = data.reply;

    } catch (error) {

        loading.textContent =
            "오류가 발생했습니다. 잠시 후 다시 시도해주세요.";

    }

    chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(text) {

    const div = document.createElement("div");
    div.textContent = text;

    return div.innerHTML;
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({
            "reply": "메시지를 입력해주세요."
        })

    try:

        response = client.responses.create(
            model="gpt-5-mini",
            instructions="""
너의 이름은 챗미나이(ChatMinai)다.

사용자의 질문에 정확하고 이해하기 쉽게 답변한다.
한국어 질문에는 기본적으로 한국어로 답변한다.
모르는 내용은 아는 척하지 않는다.
친절하지만 너무 장황하지 않게 답변한다.
""",
            input=user_message
        )

        return jsonify({
            "reply": response.output_text
        })

    except Exception as e:

        print(e)

        return jsonify({
            "reply": "AI 서버에서 오류가 발생했습니다."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
