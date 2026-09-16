import os

from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenAI API 키 확인
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("ERROR: OPENAI_API_KEY가 설정되지 않았습니다.")

client = OpenAI(api_key=api_key)


HTML = """
<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>챗미나이</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #f5f5f5;
            font-family: Arial, sans-serif;
        }

        .header {
            height: 60px;
            background: #111111;
            color: white;

            display: flex;
            align-items: center;

            padding-left: 20px;

            font-size: 22px;
            font-weight: bold;
        }

        #chat {
            height: calc(100vh - 130px);

            overflow-y: auto;

            padding: 20px;
            padding-bottom: 30px;
        }

        .message {
            max-width: 75%;

            margin-top: 12px;
            margin-bottom: 12px;

            padding: 12px 16px;

            border-radius: 15px;

            line-height: 1.5;

            white-space: pre-wrap;

            word-break: break-word;
        }

        .user {
            margin-left: auto;

            background: #222222;
            color: white;
        }

        .ai {
            margin-right: auto;

            background: white;
            color: #222222;

            border: 1px solid #eeeeee;
        }

        .input-area {
            position: fixed;

            bottom: 0;
            left: 0;

            width: 100%;

            height: 70px;

            display: flex;

            padding: 10px;

            background: white;

            border-top: 1px solid #dddddd;
        }

        #input {
            flex: 1;

            border: 1px solid #cccccc;

            border-radius: 12px;

            padding: 12px;

            font-size: 16px;

            outline: none;
        }

        #send {
            margin-left: 8px;

            padding: 0 20px;

            border: none;

            border-radius: 12px;

            background: #111111;

            color: white;

            font-size: 16px;

            cursor: pointer;
        }

        #send:disabled {
            background: #888888;
            cursor: not-allowed;
        }

    </style>
</head>


<body>

    <div class="header">
        챗미나이
    </div>


    <div id="chat">

        <div class="message ai">
            안녕하세요. 저는 챗미나이입니다. 무엇을 도와드릴까요?
        </div>

    </div>


    <div class="input-area">

        <input
            id="input"
            type="text"
            placeholder="메시지를 입력하세요."
            autocomplete="off"
        >

        <button id="send">
            전송
        </button>

    </div>


<script>

const input = document.getElementById("input");
const sendButton = document.getElementById("send");
const chat = document.getElementById("chat");


function addMessage(text, type) {

    const message = document.createElement("div");

    message.className = "message " + type;

    message.textContent = text;

    chat.appendChild(message);

    chat.scrollTop = chat.scrollHeight;

    return message;
}


async function sendMessage() {

    const message = input.value.trim();

    if (!message) {
        return;
    }

    addMessage(message, "user");

    input.value = "";

    sendButton.disabled = true;

    const loadingMessage =
        addMessage("생각 중...", "ai");


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


        if (!response.ok) {

            loadingMessage.textContent =
                data.error || "AI 서버에서 오류가 발생했습니다.";

            return;
        }


        loadingMessage.textContent =
            data.reply || "답변을 받을 수 없습니다.";


    } catch (error) {

        console.error(error);

        loadingMessage.textContent =
            "서버와 연결할 수 없습니다.";

    }


    sendButton.disabled = false;

    input.focus();

    chat.scrollTop = chat.scrollHeight;
}


sendButton.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    }
);

</script>

</body>

</html>
"""


@app.route("/")
def home():

    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "error": "잘못된 요청입니다."
            }), 400


        user_message = data.get("message", "").strip()


        if not user_message:

            return jsonify({
                "error": "메시지를 입력해주세요."
            }), 400


        if not api_key:

            return jsonify({
                "error": "OPENAI_API_KEY가 Render에 설정되지 않았습니다."
            }), 500


        response = client.responses.create(

            model="gpt-5.6-luna",

            instructions="""
너의 이름은 챗미나이(ChatMinai)다.

사용자의 질문에 정확하고 이해하기 쉽게 답변한다.

한국어 질문에는 기본적으로 한국어로 답변한다.

모르는 내용은 추측해서 사실처럼 말하지 않는다.

친절하고 자연스럽게 답변한다.

불필요하게 장황하게 답변하지 않는다.
""",

            input=user_message
        )


        answer = response.output_text


        return jsonify({
            "reply": answer
        })


    except Exception as error:

        print("OpenAI API ERROR:")
        print(error)


        return jsonify({

            "error":
                "AI 서버에서 오류가 발생했습니다. "
                "Render Logs를 확인해주세요."

        }), 500


@app.route("/health")
def health():

    return "ChatMinai OK", 200


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port

    )<div class="input-area">
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
