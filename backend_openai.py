import os
import asyncio
import json
import re
from typing import List, Optional

import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 初始化FastAPI应用
app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 根据实际需求调整
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置OpenAI API密钥（请确保在生产环境中使用安全的方式管理密钥）
os.environ["OPENAI_API_KEY"] = "sk-EUvJyR1lj5XLErzh509b4eFe97F1412a8d8720Fa7fBd6874"
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise EnvironmentError("请设置环境变量 OPENAI_API_KEY")

# 预设问题
QUESTIONS = [
    {
        "id": "preprompt_age",
        "question": "您的年龄段：",
        "options": ["20岁以下", "20-30岁", "30-40岁", "40-50岁"]
    },
    {
        "id": "preprompt_gender",
        "question": "您的性别：",
        "options": ["男", "女"]
    },
    {
        "id": "preprompt_symptom",
        "question": "您想要改善什么问题：",
        "options": ["未病先防", "既病防变", "瘥后防复"]
    }
]

# 体质学说知识库内容
CONSTITUTION_KNOWLEDGE_BASE = """
4.1 平和质

内涵

定义 平和质指一种强健、壮实的体质状态，表现为体态适中、面色红润、精力充沛。

体质特征

形体特征：体形匀称健壮。
常见表现：
面色、肤色润泽
头发稠密有光泽
目光有神
鼻色明润，嗅觉通利
口和，唇色红润
不易疲劳，精力充沛
耐受寒热
睡眠良好
胃纳佳（食欲良好）
二便正常
舌色淡红，苔薄白
脉和有神
心理特征：性格随和开朗。
发病倾向：平素较少患病。
环境适应能力：对自然和社会环境的适应能力较强。
成因 先天禀赋良好，后天调养得当。

文献依据

古代文献

命名依据：称为“阴阳和平之人”或“平人”。
特征描述：
《素问·调经论》：“阴阳匀平，以充其形，九候若一，命曰平人。”
《灵枢·天年》：“五脏坚固，血脉和调，肌肉解利，皮肤致密……故能长久。”
形成因素：阴阳调和，血脉调畅。
现代文献 体形匀称健壮，精力充沛，毛发稠密有光泽，面色红润，目光有神，耐受寒热，胃纳佳，睡眠良好，二便正常，舌质淡红，苔薄白，脉象和缓。

4.2 气虚质

内涵

定义 因元气不足，表现为气息低弱、机体及脏腑功能低下的体质状态。

体质特征

形体特征：肌肉不健壮，瘦人为多。
常见表现：
平素语音低怯，气短懒言
肢体容易疲乏，精神不振
易出汗，自汗
面色偏黄或白，目光少神
头晕，健忘
舌淡红，舌体胖大，边有齿痕
脉象虚缓
大便正常或不成形，小便正常或偏多
心理特征：性格内向，情绪不稳定，胆小，不喜欢冒险。
发病倾向：易患感冒，病后康复慢，易患内脏下垂、虚劳等病。
环境适应能力：不耐受寒邪、风邪、暑邪。
成因 先天本弱，后天失养，或病后气亏。

文献依据

古代文献

命名依据：称为“气弱”、“气衰”或“气虚之人”。
特征描述：
《景岳全书》：“肥人多气虚之证。”
《医原》：“其人肥白，多属气虚。”
发病倾向：易感风邪，表气素虚。
形成因素：禀赋不足，受父母体弱影响。
现代文献 面色偏黄或白，毛发不华，气短懒言，易疲乏，舌淡红，边有齿痕，脉虚缓，易患外感。

4.3 阳虚质

内涵

定义 因阳气不足，以虚寒现象为主要特征的体质状态。

体质特征

形体特征：形体白胖、肌肉不壮。
常见表现：
平素畏冷，手足不温
喜热饮食
精神不振，睡眠偏多
面色柔白，唇色淡
舌淡胖嫩，苔白润
脉象沉迟而弱
大便溏薄，小便清长
心理特征：性格沉静，内向。
发病倾向：易患寒证，如痰饮、肿胀、泄泻、阳痿。
环境适应能力：不耐寒邪，耐夏不耐冬，易感湿邪。
成因 先天不足，或病后阳气亏虚。

文献依据

古代文献

命名依据：称为“阳虚之质”。
特征描述：
《素问·调经论》：“阳虚则外寒。”
《医学心悟》：“阴脏者阳必虚，阳虚者多寒。”
发病倾向：易患湿邪，湿甚则阳微。
形成因素：先天阳气不足，或生冷内伤。
现代文献 面色白，畏冷，手足不温，喜热饮食，舌淡胖嫩，苔白润，脉沉迟而弱。

4.4 阴虚质

内涵

定义 体内津液、精血等阴液亏少，以阴虚内热为主要特征的体质状态。

体质特征

形体特征：体形瘦长。
常见表现：
手足心热，易口燥咽干
面色潮红，有烘热感
睡眠差，心烦易怒
舌红少津少苔
大便干燥，小便短涩
脉象细弦或数
心理特征：性情急躁，外向好动。
发病倾向：易患阴虚燥热病变。
环境适应能力：不耐热邪，耐冬不耐夏，不耐受燥邪。
成因 先天不足，久病失血，纵欲耗精，积劳伤阴。

文献依据

古代文献

命名依据：称为“阴虚之质”。
特征描述：
《素问·调经论》：“阴虚则内热。”
《格致余论》：“瘦人火多。”
发病倾向：易患阳盛阴虚之候，或病阳毒。
形成因素：先天阴虚，脏腑燥热。
现代文献 体形瘦长，手足心热，口燥咽干，面色潮红，舌红少苔，脉细数，易烦躁。

4.5 痰湿质

内涵

定义 由于水液内停、痰湿凝聚，以黏滞重浊为主要特征的体质状态。

体质特征

形体特征：体形肥胖，腹部肥满松软。
常见表现：
面部皮肤油脂较多，多汗且黏
胸闷，痰多
易困倦，身重不爽
舌体胖大，苔白腻
口黏腻或甜
大便正常或不实，小便不多或微混
心理特征：性格偏温和稳重，善于忍耐。
发病倾向：易患消渴、中风、胸痹等病证。
环境适应能力：对梅雨季节及湿环境适应能力差。
成因 先天遗传或后天过食肥甘。

文献依据

古代文献

命名依据：称为“肥人”、“脂人”。
特征描述：
《格致余论》：“肥人多痰”、“肥人湿多”。
发病倾向：易患消渴、胸痹等。
形成因素：“肥美之所发也”，过食甘肥。
现代文献 体形肥胖，面部多油，痰多，易困倦，舌胖大，苔白腻，脉滑。

4.6 湿热质

内涵

定义 以湿热内蕴为主要特征的体质状态。

体质特征

形体特征：形体偏胖或瘦削。
常见表现：
面垢油光，易生痤疮粉刺
口苦口干，身重困倦
心烦懈怠，眼睛红赤
舌质偏红，苔黄腻
大便燥结或黏滞，小便短赤
心理特征：性格多急躁易怒。
发病倾向：易患疮疖、黄疸、火热等病证。
环境适应能力：对湿热环境适应能力差，尤其在夏末秋初。
成因 先天禀赋、久居湿地、喜食肥甘或长期饮酒。

文献依据

古代文献

命名依据：称为“素禀湿热”。
特征描述：
《素问·生气通天论》：“膏梁之变，足生大疔。”
发病倾向：易患黄疸、疔疮等。
形成因素：久居湿地，饮食不节。
现代文献 面垢油光，易生痤疮，口苦，舌红苔黄腻，脉滑数。

4.7 瘀血质

内涵

定义 体内血液运行不畅，有瘀血内阻的体质状态。

体质特征

形体特征：多为瘦人。
常见表现：
面色晦暗，皮肤偏暗或色素沉着
易出现瘀斑，易患疼痛
口唇暗淡或紫
舌质暗，有瘀点或瘀斑，舌下静脉曲张
脉象细涩或结代
心理特征：性格易烦躁，健忘。
发病倾向：易患出血、瘕、中风、胸痹等病。
环境适应能力：不耐受风邪、寒邪。
成因 先天禀赋不足、后天损伤、忧郁气滞、久病入络等。

文献依据

古代文献

命名依据：称为“素有恶血在内”。
特征描述：
《灵枢·逆顺肥瘦》：“其血黑以浊，其气涩以迟。”
发病倾向：易患中风、胸痹等。
形成因素：跌扑损伤，七情内伤，久病入络，年老致瘀。
现代文献 面色晦暗，口唇紫暗，舌质青紫或有瘀斑，舌下静脉曲张，脉细涩。

4.8 气郁质

内涵

定义 长期情志不畅、气机郁滞形成的体质状态。

体质特征

形体特征：多为瘦人。
常见表现：
性格内向不稳定，忧郁脆弱，敏感多疑
胸胁胀满，善太息
睡眠较差，食欲减退
舌淡红，苔薄白，脉弦细
心理特征：性格内向，情绪不稳定。
发病倾向：易患郁症、脏躁、梅核气等病。
环境适应能力：对精神刺激适应能力差，不喜欢阴雨天气。
成因 先天遗传，精神刺激，忧郁思虑过度。

文献依据

古代文献

命名依据：称为“易伤以忧”。
特征描述：
《医学正传》：“或因怒气伤肝，或因惊气入胆。”
发病倾向：易患郁结、生痰等病。
形成因素：体形与脏腑禀赋不同，情志不畅。
现代文献 性格忧郁，胸胁胀满，善太息，舌淡红，脉弦细。

4.9 特禀质

内涵

定义 由于先天性和遗传因素造成的体质缺陷，包括先天性、遗传性疾病和过敏体质等。

体质特征

形体特征：无特殊，或有畸形，或先天生理缺陷。
常见表现：
遗传性疾病具有垂直遗传、先天性、家族性特征
过敏体质者易过敏反应
心理特征：因个体情况而异。
发病倾向：易患过敏性疾病、遗传性疾病、胎传性疾病等。
环境适应能力：适应能力差，易引发宿疾。
成因 先天因素、遗传因素、环境因素、药物因素等。

文献依据

古代文献

命名依据：称为“禀赋”、“禀性”、“胎禀”等。
特征描述：
《幼幼新书》：“禀赋也，体有刚柔、脉有强弱、气有多寡、血有盛衰。”
发病倾向：易患先天性疾病、过敏性疾病等。
形成因素：先天遗传，母体影响。
现代文献 体形无特殊，或有畸形，或先天生理缺陷；遗传性疾病具有垂直遗传、先天性、家族性特征；过敏体质者易过敏反应。
"""

# 疾病知识库
DISEASES_KNOWLEDGE_BASE = """
中医针对糖尿病的治疗主要是通过辨证论治的方式，根据不同病人所表现出的临床症状，主要分为上消、中消以及下消等三大类型
上消(肺热津伤)
①病人主要表现为口舌干燥，饮水量增多，并且经常会出现口渴的现象，尿量增多，烦热，多汗，舌苔薄黄，舌尖红，脉洪数。
②治疗以生津止渴、润肺清热为主。

中消
(1)胃热炽盛。
①病人主要表现为形体比较瘦弱，饮食量大，但是很容易饥饿，大便干燥，经常口渴，小便频数，舌质红，苔黄燥，脉细数。
②治疗以养阴增液，泻火清胃为主。
(2)气阴亏虚。
①病人主要表现为经常口渴，大便溏薄，食欲减退，腹胀，四肢无力，精神萎靡，形体瘦弱，舌淡红，苔白，脉弱。
②治疗以止渴生津，健脾益气为主。

下消
(1)肾阴亏虚。
①病人主要表现出尿量增多，但是尿液浑浊，如膏脂状，腰膝酸软，耳鸣,头晕，四肢乏力，口舌干燥，皮肤干燥，骨蒸潮热，五心烦热，遗精盗汗，舌质较红，舌苔较少，脉细数等症状。
②治疗以滋阴固肾为主。
(2)阴阳两虚。
①病人主要表现出尿量增多，面容憔悴，腰膝酸软，畏寒肢冷，四肢厥冷，耳轮干枯，舌质淡，苔白，脉沉细无力的症状。
②治疗主要以补肾固摄，滋阴温阳为主。

冠心病
證型：痰濁痹阻
證候特點：胸悶如窒，痛引肩背，氣短喘促，多形體肥胖，肢體沉重，或伴咳痰，舌苔厚膩
治法:寬胸化痰，通陽泄濁

證型：心脈瘀阻
證候特點：心胸刺痛，部位固定，入夜尤甚，心悸不寧，舌質紫黯，或有瘀點
治法:活血化瘀，通脈止痛


"""

# 穴位库
ACUPOINT_BASE = """
        "1-鱼际穴-促进肺气，缓解咳嗽、哮喘，帮助改善呼吸系统功能。"
        "2-踝穴-活络通经，缓解手腕疼痛和关节不适。"
        "4-少商穴-清热解毒，适用于口腔溃疡、喉咙痛等。"
        "5-咳喘穴-止咳平喘，对支气管炎、过敏性咳嗽有帮助。"
        "6-小肠穴-促进消化，适用于腹痛、腹泻等消化系统问题。"
        "7-大肠穴-调理肠道，帮助便秘和腹泻。"
        "10-三焦穴-疏通气机，调节水液代谢，适合浮肿等问题。"
        "11-心穴-镇静安神，缓解心脏不适和焦虑。"
        "12-中冲穴-清心解热，适用于中暑、口渴等症状。"
        "14-肝穴-疏肝解郁，适用于情绪抑郁、月经不调等。"
        "15-肺穴-补肺气，适合呼吸系统疾病。"
        "18-命门穴-补肾阳，适合肾虚、腰痛等症状。"
        "19-肾穴-调节水液代谢，适合肾功能减退、浮肿等问题。"
        "20-少泽穴-清热解毒，适用于发热、喉咙痛等。"
"""

# WebSocket消息模型
class Message(BaseModel):
    type: str
    data: Optional[dict] = None
    message: Optional[str] = None


# 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"Client disconnected: {websocket.client}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending message to client: {e}")
                self.disconnect(connection)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message to client: {e}")
            self.disconnect(websocket)


manager = ConnectionManager()

# 新增：激光设备连接管理器
class LaserConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Laser device connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"Laser device disconnected: {websocket.client}")

    async def send_to_lasers(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error sending message to laser device: {e}")
                self.disconnect(connection)


# 实例化激光设备连接管理器
laser_manager = LaserConnectionManager()

# 初始化SHOW_KEYPOINT_ID为空列表
# SHOW_KEYPOINT_ID: List[int] = []
SHOW_KEYPOINT_ID = [6,7,8]

async def call_openai_api(messages: List[dict]) -> str:
    """
    调用OpenAI API并返回响应内容。
    """
    try:
        response = await asyncio.to_thread(
            requests.post,
            "https://aihubmix.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.95,
                "top_p": 0.7,
                "frequency_penalty": 1
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"调用OpenAI API时出错: {e}")
        return f"错误: 无法从AI模型获取响应。{str(e)}"


def generate_initial_message_and_prompt(answers: dict) -> (str, str):
    """
    根据预设问题的答案生成初始消息和提示语。
    """
    initial_message = (
        f"您好，根据问题我了解到您的性别为{answers['preprompt_gender']}，"
        f"年龄段{answers['preprompt_age']}，想要进行{answers['preprompt_symptom']}，"
        f"接下来请您更加详细的描述您的症状。"
    )

    prompt = (
        f"你是一位中医专家，同时是大型医院的中医主治医生，你正在门诊进行坐诊。下面的资料是最新的关于中医体质学说的论文。\n"
        f"{CONSTITUTION_KNOWLEDGE_BASE}\n"
        f"首先请你阅读该论文，并对其进行理解吸收。随后请你根据该论文中的内容，"
        f"经过五轮与用户的问诊，旨在通过这些问诊对所有人群进行体质分类。\n"
        f"请注意你的问诊应当围绕下方论文中的方向进行，围绕论文中的体质判断方法，准确的判断出该用户的体质。\n\n"
        f"要求由你发起提问。当你经过五轮提问后，需要确定用户属于这九种体质中的某一种，并且严格按照下面这样的方式给出结论（阴虚质只是一个示例）：\n\n"
        f"<用户体质：阴虚质>\n\n"
        f"接下来第一条消息，你应该向用户问好，你已经得到了ta的年龄段为{answers['preprompt_age']}，性别为{answers['preprompt_gender']}，这次前往门诊是想要想要进行{answers['preprompt_symptom']}，请根据这些信息开始问诊。\n\n"
        f"在问诊结束后，大模型应当会像上方格式一样输出包含<用户体质：阴虚质>的回话，并且结合论文与用户回答，向用户介绍该体质。\n\n"
        f"请注意专注于您的角色，当用户询问与本次问诊无关的话题时，您需要将话题引到会问诊本身，并同时拒绝回答无关问题。"
    )

    return initial_message, prompt

def generate_followup_prompt() -> str:
    """
    生成体质确定后的后续问诊和针灸处方的提示语。
    """
    followup_prompt = f"""
        你是一位经验丰富的中医师，熟悉中医理论和针灸治疗。你已经掌握了患者的基本信息，包括年龄、性别以及中医体质分类。现在，你将进行正式的问诊环节。
        
        1. **问诊阶段：**
            - 请根据患者的基本信息，及用户体质，首先询问其病史、现病情况、生活习惯等相关信息。
            - 在问诊过程中，结合中医疾病知识库和患者的具体状况，进行针对性的讲解与科普，帮助患者理解自己的健康状况。
            - 你应当直接进入问诊环节，无需与用户进行问候。
            - 中医疾病知识库如下：
            ```
            {DISEASES_KNOWLEDGE_BASE}
            ```
            - 你可以参考以下穴位及其功效进行诊断和治疗：
            ```
            {ACUPOINT_BASE}
            ```
        
        2. **针灸处方阶段：**
            - 在完成问诊后，结合前述中医疾病知识库和穴位信息以及病人信息和体质，制定最佳的针灸处方。
            - 处方应严格为三个穴位。
            - 处方应严格按照以下格式给出，每个穴位占一行：
                ```
                [穴位编号]. <穴位名称> - <功效描述> - <针灸时间>
                ```
              例如：
                ```
                0. <大陵穴> - <调节心脏功能，缓解心悸、失眠和焦虑。> - <针灸时间3分钟>
                7. <大肠穴> - <调理肠道，帮助便秘和腹泻。> - <针灸时间3分钟>
                ```
            - 请勿添加任何额外的标注信息或排序。
        
        3. **治疗方案介绍：**
            - 向患者详细介绍你的治疗方案，包括针灸的具体穴位、每个穴位的功效以及治疗的预期效果。
            - 在介绍过程中，结合患者的具体情况，进行针对性的解释和科普，确保患者理解并信任你的治疗方案。
        
        请严格遵守以上步骤和格式要求，确保问诊和处方的专业性与规范性。
        """
    return followup_prompt


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket端点，用于处理用户对话。
    """
    await manager.connect(websocket)
    messages = []
    user_constitution = None  # 存储用户体质
    prescriptions = []  # 存储针灸处方
    conversation_phase = 1  # 1: 体质确定阶段, 2: 针灸处方阶段

    try:
        # 发送预设问题给客户端
        await manager.send_personal_message({"type": "questions", "data": QUESTIONS}, websocket)

        while True:
            data = await websocket.receive_json()
            print(f"收到消息: {data}")

            if data["type"] == "preprompt_complete":
                preprompt_answers = data["answers"]
                initial_message, prompt = generate_initial_message_and_prompt(preprompt_answers)
                messages.append({"role": "system", "content": prompt})

                # 由大模型首先发起对话
                ai_initial_message = await call_openai_api(messages)
                messages.append({"role": "assistant", "content": ai_initial_message})
                await manager.send_personal_message({"type": "ai_response", "data": ai_initial_message}, websocket)

            elif data["type"] == "chat":
                user_message = data.get("message", "").strip()
                if not user_message:
                    continue  # 忽略空消息

                messages.append({"role": "user", "content": user_message})
                response_text = await call_openai_api(messages)

                # 打印AI的响应内容以便调试
                print(f"AI响应内容: {response_text}")

                if conversation_phase == 1:
                    # 检查并提取用户体质
                    match = re.search(r"<用户体质：(.+?)>", response_text)
                    if match:
                        user_constitution = match.group(1)
                        print(f"用户体质已确定为：{user_constitution}")
                        # 从 response_text 中移除 <用户体质：...> 部分
                        response_text = re.sub(r"<用户体质：.+?>", "", response_text).strip()
                        messages.append({"role": "assistant", "content": response_text})
                        await manager.send_personal_message({"type": "ai_response", "data": response_text}, websocket)

                        # 发送初始消息提示用户进入下一阶段
                        next_phase_message = "很好，现在我们已经得知了您的体质，请继续完成下一阶段。"
                        await manager.send_personal_message({"type": "initial_message", "data": next_phase_message},
                                                            websocket)

                        # 更新对话阶段
                        conversation_phase = 2

                        # 生成新的 prompt 并添加为系统消息
                        followup_prompt = generate_followup_prompt()
                        messages.append({"role": "system", "content": followup_prompt})

                        # 由大模型发起下一阶段的对话
                        ai_followup_message = await call_openai_api(messages)
                        messages.append({"role": "assistant", "content": ai_followup_message})
                        await manager.send_personal_message({"type": "ai_response", "data": ai_followup_message},
                                                            websocket)
                    else:
                        # 如果未检测到体质信息，继续正常对话
                        messages.append({"role": "assistant", "content": response_text})
                        await manager.send_personal_message({"type": "ai_response", "data": response_text}, websocket)

                elif conversation_phase == 2:
                    # 在针灸处方阶段，继续处理对话
                    messages.append({"role": "assistant", "content": response_text})
                    await manager.send_personal_message({"type": "ai_response", "data": response_text}, websocket)

                    # 使用更新后的正则表达式匹配所有符合格式的针灸处方，并捕获ID
                    # 示例格式：1. <百会穴> - <调节神经系统> - <针灸时间3分钟>
                    prescription_matches = re.findall(r"(\d+)\.\s*<(.+?)>\s*-\s*<(.+?)>\s*-\s*<针灸时间(\d+)分钟>",
                                                      response_text)

                    if prescription_matches:
                        for match in prescription_matches:
                            prescription_id = int(match[0])
                            acupoint = match[1]
                            function = match[2]
                            time_minutes = int(match[3])
                            prescriptions.append({
                                "id": prescription_id,
                                "acupoint": acupoint,
                                "function": function,
                                "time_minutes": time_minutes
                            })
                        print(f"针灸处方已记录：{prescriptions}")

                        # 动态设置SHOW_KEYPOINT_ID为当前会话的所有处方ID
                        global SHOW_KEYPOINT_ID
                        SHOW_KEYPOINT_ID = [p['id'] for p in prescriptions]
                        print(f"SHOW_KEYPOINT_ID已更新为：{SHOW_KEYPOINT_ID}")

                        # 发送处方结束消息，包含用户体质和所有针灸处方
                        await manager.send_personal_message({
                            "type": "session_end",
                            "data": {
                                "constitution": user_constitution,
                                "prescriptions": prescriptions
                            }
                        }, websocket)
                        break  # 结束当前连接

            else:
                # 处理其他类型的对话（如果有）
                messages.append({"role": "assistant", "content": response_text})
                await manager.send_personal_message({"type": "ai_response", "data": response_text}, websocket)

    except WebSocketDisconnect:
        print("WebSocket断开连接")
    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        manager.disconnect(websocket)


# 新增：激光设备的 WebSocket 端点
@app.websocket("/ws/laser")
async def websocket_laser_endpoint(websocket: WebSocket):
    """
    WebSocket端点，用于激光设备连接。
    """
    await laser_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 如果需要处理来自激光设备的消息，可以在这里添加逻辑
            print(f"收到来自激光设备的消息: {data}")
    except WebSocketDisconnect:
        print("Laser WebSocket断开连接")
    except Exception as e:
        print(f"Laser WebSocket错误: {e}")
    finally:
        laser_manager.disconnect(websocket)
        await websocket.close()


# 修改后的 /ws/keypoints 端点
# @app.websocket("/ws/keypoints")
# async def websocket_keypoints(websocket: WebSocket):
#     """
#     WebSocket端点，用于接收和广播机器视觉端发送的关键点数据。
#     """
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_json()
#             keypoints_data = data.get('keypoints', {})
#             if keypoints_data:
#                 # 根据动态的 SHOW_KEYPOINT_ID 过滤关键点
#                 filtered_keypoints = {
#                     k: v for k, v in keypoints_data.items()
#                     if int(k.split('_')[1]) in SHOW_KEYPOINT_ID
#                 }
#                 if filtered_keypoints:
#                     # 广播给所有连接的客户端
#                     message = {"type": "keypoint_data", "data": filtered_keypoints}
#                     await manager.broadcast(message)
#
#                     # 新增：将关键点数据格式化并发送给激光设备
#                     laser_format = ""
#                     for idx, (key, coord) in enumerate(filtered_keypoints.items()):
#                         x = coord.get('x')
#                         y = coord.get('y')
#                         if x is None or y is None:
#                             continue  # 跳过缺失的坐标
#                         try:
#                             x = int(float(x))
#                             y = int(float(y))
#                         except ValueError:
#                             print(f"无效的坐标值: x={x}, y={y}")
#                             continue  # 跳过无效的坐标
#
#                         # 确保x和y在0-99范围内
#                         x = max(0, min(99, x))
#                         y = max(0, min(99, y))
#
#                         # 添加id并格式化为 [x][y]
#                         laser_format += f"{x:02}{y:02}"
#
#                     # 在laser_format末尾添加 \r
#                     if laser_format:
#                         laser_format += '\r'
#                         # ser.write(laser_format)
#                         print(f"发送给激光设备的格式化数据: {laser_format}")
#                         await laser_manager.send_to_lasers(laser_format)

from collections import defaultdict


# 定义 EMA 的平滑因子
ALPHA = 0.5  # 可以根据需要调整，范围 (0, 1)

# 使用 defaultdict 存储每个关键点的当前 EMA 值
# key: 关键点ID, value: {'x': 当前 EMA x, 'y': 当前 EMA y}
keypoint_ema = defaultdict(lambda: {'x': None, 'y': None})



@app.websocket("/ws/keypoints")
async def websocket_keypoints(websocket: WebSocket):
    """
    WebSocket端点，用于接收和广播机器视觉端发送的关键点数据。
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            keypoints_data = data.get('keypoints', {})
            if keypoints_data:
                # 根据动态的 SHOW_KEYPOINT_ID 过滤关键点
                filtered_keypoints = {
                    k: v for k, v in keypoints_data.items()
                    if int(k.split('_')[1]) in SHOW_KEYPOINT_ID
                }
                if filtered_keypoints:
                    # 广播给所有连接的客户端
                    message = {"type": "keypoint_data", "data": filtered_keypoints}
                    await manager.broadcast(message)

                    # 初始化用于格式化激光设备的数据
                    laser_format = ""
                    for key, coord in filtered_keypoints.items():
                        x = coord.get('x')
                        y = coord.get('y')
                        if x is None or y is None:
                            continue  # 跳过缺失的坐标
                        try:
                            x = int(float(x))
                            y = int(float(y))
                        except ValueError:
                            print(f"无效的坐标值: x={x}, y={y}")
                            continue  # 跳过无效的坐标

                        # 确保x和y在0-99范围内
                        x = max(0, min(99, x))
                        y = max(0, min(99, y))

                        # 应用 EMA 滤波
                        if keypoint_ema[key]['x'] is None:
                            # 如果是第一次接收该关键点的数据，初始化 EMA
                            keypoint_ema[key]['x'] = x
                            keypoint_ema[key]['y'] = y
                        else:
                            # 计算 EMA
                            keypoint_ema[key]['x'] = ALPHA * x + (1 - ALPHA) * keypoint_ema[key]['x']
                            keypoint_ema[key]['y'] = ALPHA * y + (1 - ALPHA) * keypoint_ema[key]['y']

                        # 将 EMA 值转换为整数
                        avg_x = int(keypoint_ema[key]['x'])
                        avg_y = int(keypoint_ema[key]['y'])

                        # 再次确保平均值在0-99范围内
                        avg_x = max(0, min(99, avg_x))
                        avg_y = max(0, min(99, avg_y))

                        # 格式化为 [x][y]，确保每个坐标为两位数
                        laser_format += f"{avg_x:02}{avg_y:02}"

                    # 在laser_format末尾添加 \r
                    if laser_format:
                        laser_format += '\r'
                        # ser.write(laser_format)
                        print(f"发送给激光设备的格式化数据: {laser_format}")
                        await laser_manager.send_to_lasers(laser_format)
    except Exception as e:
        print(f"WebSocket连接错误: {e}")
    finally:
        await manager.disconnect(websocket)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        timeout_keep_alive=3600,  # 保持连接 1 小时
        ws_ping_interval=60,  # 每 60 秒发送一次 ping
        ws_ping_timeout=30,  # 30 秒未收到 pong 则超时
    )
