let socket;
let keypointSocket;
let currentQuestionIndex = 0;
let questions = [];
let prepromptAnswers = {};
let currentStage = 1; // 初始阶段为1

// 定义关键点信息映射表
const KEYPOINTS_INFO = {
    0: { name: "大陵穴", function: "调节心脏功能，缓解心悸、失眠和焦虑" },
    1: { name: "鱼际穴", function: "促进肺气，缓解咳嗽、哮喘，帮助改善呼吸系统功能" },
    2: { name: "踝穴", function: "活络通经，缓解手腕疼痛和关节不适" },
    4: { name: "少商穴", function: "清热解毒，适用于口腔溃疡、喉咙痛等" },
    5: { name: "咳喘穴", function: "止咳平喘，对支气管炎、过敏性咳嗽有帮助" },
    6: { name: "小肠穴", function: "促进消化，适用于腹痛、腹泻等消化系统问题" },
    7: { name: "大肠穴", function: "调理肠道，帮助便秘和腹泻" },
    10: { name: "三焦穴", function: "疏通气机，调节水液代谢，适合浮肿等问题" },
    11: { name: "心穴", function: "镇静安神，缓解心脏不适和焦虑" },
    12: { name: "中冲穴", function: "清心解热，适用于中暑、口渴等症状" },
    14: { name: "肝穴", function: "疏肝解郁，适用于情绪抑郁、月经不调等" },
    15: { name: "肺穴", function: "补肺气，适合呼吸系统疾病" },
    18: { name: "命门穴", function: "补肾阳，适合肾虚、腰痛等症状" },
    19: { name: "肾穴", function: "调节水液代谢，适合肾功能减退、浮肿等问题" },
    20: { name: "少泽穴", function: "清热解毒，适用于发热、喉咙痛等" }
};

window.onload = function() {
    document.getElementById('welcomePage').style.display = 'block';
    updateProgressIndicator(1);
}

function updateProgressIndicator(stage) {
    currentStage = stage;
    for (let i = 1; i <= 5; i++) {
        const step = document.getElementById(`step${i}`);
        if (step) { // 确保元素存在
            if (i <= stage) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        }
    }
}

function startDiagnosis() {
    document.getElementById('welcomePage').style.display = 'none';
    document.getElementById('questionContainer').style.display = 'block';
    connectWebSocket();
}

function connectWebSocket() {
    socket = new WebSocket('ws://localhost:9000/ws');

    socket.onopen = function(e) {
        console.log("[open] 连接已建立");
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === "questions") {
            questions = data.data;
            showNextQuestion();
        } else if (data.type === "ai_response") {
            addMessage("知络医诊", data.data);
        } else if (data.type === "initial_message") {
            addMessage("系统", data.data);
        }
    };

    socket.onclose = function(event) {
        console.log('[close] 连接已断开');
    };

    socket.onerror = function(error) {
        console.log(`[error] ${error.message}`);
    };
}

function connectKeypointWebSocket() {
    keypointSocket = new WebSocket('ws://localhost:9000/ws/keypoints');

    keypointSocket.onopen = function(e) {
        console.log("[Keypoint WebSocket] 连接已建立");
    };

    keypointSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === "keypoint_data") {
            handleKeypointData(data.data);
        }
    };

    keypointSocket.onclose = function(event) {
        console.log('[Keypoint WebSocket] 连接已断开');
    };

    keypointSocket.onerror = function(error) {
        console.log(`[Keypoint WebSocket error] ${error.message}`);
    };
}

function showNextQuestion() {
    const questionContainer = document.getElementById('questionContainer');
    if (currentQuestionIndex < questions.length) {
        const question = questions[currentQuestionIndex];
        let html = `<h2>${question.question}</h2>`;
        question.options.forEach(option => {
            html += `<button class="option" onclick="handleOptionClick('${option}')">${option}</button>`;
        });
        questionContainer.innerHTML = html;
    } else {
        questionContainer.style.display = 'none';
        document.getElementById('chatInterface').style.display = 'block';
        document.getElementById('videoContainer').style.display = 'block';
        socket.send(JSON.stringify({type: "preprompt_complete", answers: prepromptAnswers}));

        updateProgressIndicator(2); // 更新为步骤2

        // 在 videoContainer 显示后，调用 connectKeypointWebSocket()
        connectKeypointWebSocket();
    }
}

function handleOptionClick(selectedValue) {
    const currentQuestion = questions[currentQuestionIndex];
    prepromptAnswers[currentQuestion.id] = selectedValue;
    currentQuestionIndex++;
    showNextQuestion();
}

document.getElementById('sendMessage').addEventListener('click', sendMessage);
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;
    if (message && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({type: "chat", message: message}));
        addMessage("您", message);
        messageInput.value = '';
    }
}

function addMessage(sender, message) {
    const chatbox = document.getElementById('chatbox');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(sender === "您" ? 'user-message' : 'ai-message');

    const senderSpan = document.createElement('span');
    senderSpan.classList.add('message-sender');
    senderSpan.textContent = sender + ": ";

    const contentSpan = document.createElement('span');
    contentSpan.classList.add('message-content');

    if (sender !== "您") {
        // 如果是AI消息，解析Markdown
        const htmlContent = marked.parse(message);
        contentSpan.innerHTML = htmlContent;
    } else {
        // 如果是用户消息，直接设置文本内容
        contentSpan.textContent = message;
    }

    messageElement.appendChild(senderSpan);
    messageElement.appendChild(contentSpan);

    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight;
}


function handleKeypointData(keypointsData) {
    const coordContainer = document.getElementById('keypointCoordinatesContainer');
    coordContainer.innerHTML = '';

    for (const keypointID in keypointsData) {
        const keypoint = keypointsData[keypointID];
        const idNumber = parseInt(keypointID.split('_')[1], 10);

        // 获取关键点信息
        const keypointInfo = KEYPOINTS_INFO[idNumber];

        if (keypointInfo) {
            const name = keypointInfo.name;
            const func = keypointInfo.function;
            const x = keypoint.x;
            const y = keypoint.y;

            const coordElement = document.createElement('p');
            coordElement.textContent = `${name}：${func}，坐标：x=${x}, y=${y}`;
            coordContainer.appendChild(coordElement);
        } else {
            // 如果关键点ID未在映射表中定义，可以选择显示默认信息或跳过
            const x = keypoint.x;
            const y = keypoint.y;

            const coordElement = document.createElement('p');
            coordElement.textContent = `关键点 ${idNumber} 坐标：x=${x}, y=${y}`;
            coordContainer.appendChild(coordElement);
        }
    }
}

/* 未来步骤4和步骤5的触发点可以在相应的功能开发完成后添加 */

function startAcupuncture() {
    // 开始针灸的相关逻辑
    updateProgressIndicator(4);
}

function finishAcupuncture() {
    // 完成针灸的相关逻辑
    updateProgressIndicator(5);
}
