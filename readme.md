# 项目说明

> CCCC-AI 2024参赛作品：文心大模型驱动的家用激光针灸机器人（作品：IDAIPP000677）
> 
> 本Notebook文档是CCCC-AI 2024参赛作品的在线文档。项目整体目标是构建一个由文心大模型驱动的家用激光针灸机器人，通过自动化诊疗与治疗方案，实现个性化的中医激光针灸治疗。

项目已在本地构建部署完成，并将主要内容部署（及开源）于[AI Studio 星河社区](https://aistudio.baidu.com/overview)中，欢迎各位同学**体验+fork** ！

# 项目完成情况（部署及开源）汇总

<table border="1" style="border-collapse: collapse; width: 100%;">
  <tr>
    <th style="text-align: center;">编号</th>
    <th style="text-align: center;">模块</th>
    <th style="text-align: center;">内容描述</th>
    <th style="text-align: center;">完成情况</th>
  </tr>
  <tr>
    <td style="text-align: center;" rowspan="2">1</td>
    <td style="text-align: center;" rowspan="2">「知络医诊」问诊模块</td>
    <td>「知络医诊」具备体质辨析、疾病证候分型和针灸处方生成功能</td>
    <td>Streamlit部署<br><a href="http://static-ae1rcae0a.aistudio-app.com/" style="background-color: yellow; padding: 2px; border-radius: 4px; color: red">[点击跳转AI-Studio🔗]</a></td>
  </tr>
  <tr>
    <td>针灸知识图谱：覆盖20余种常见疾病的证候分型和针灸处方</td>
    <td>持续完善</td>
  </tr>
  <tr>
    <td style="text-align: center;" rowspan="2">2</td>
    <td style="text-align: center;" rowspan="2">穴位关键点检测模块</td>
    <td>基于PaddleDetection的二阶段穴位关键点检测模型，<br>包含完整训练过程及权重</td>
    <td>训练过程开源<br><a href="https://aistudio.baidu.com/projectdetail/8375903" style="background-color: yellow; padding: 2px; border-radius: 4px; color: red">[点击跳转AI-Studio🔗]</a></td>
  </tr>
  <tr>
    <td>手部穴位关键点检测数据集（微调数据集）</td>
    <td>EasyDL标注完成</td>
  </tr>
  <tr>
    <td style="text-align: center;" rowspan="2">3</td>
    <td style="text-align: center;" rowspan="2">高精度激光控制模块</td>
    <td>激光振镜、摄像头及外围PCB电路设计</td>
    <td>已完成</td>
  </tr>
  <tr>
    <td>基于STM32的激光振镜驱动程序</td>
    <td>已完成</td>
  </tr>
  <tr>
    <td style="text-align: center;">4</td>
    <td style="text-align: center;">边缘计算设备部署</td>
    <td>NVIDIA Jetson Nano 实现边缘部署与集成</td>
    <td>已本地部署</td>
  </tr>
</table>




# 项目概述与背景介绍

## 选题背景

随着人们对健康管理和疾病预防意识的提高，传统中医针灸技术逐渐从治疗手段扩展到家庭健康管理与慢病防控等应用场景中。其中，激光针灸技术作为中医针灸的现代化延伸，因其无创、安全和便捷等特点，逐渐受到关注。激光针灸通过低强度激光束照射腧穴，能够有效刺激经络、调理脏腑，并改善人体气血循环，适用于多种慢性病的预防和康复。

然而，传统针灸技术在实际应用中仍存在多个痛点，如穴位定位的准确性依赖于医师经验、治疗过程繁琐、患者需要频繁往返医疗机构等问题，这在一定程度上制约了针灸技术在家庭和个人健康管理领域的广泛应用。此外，传统激光针灸设备通常缺乏智能化和个性化调控能力，无法根据不同患者的体质、病情特点进行动态调整，从而影响治疗效果。

## 项目目标

<img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/01-%E5%B0%81%E9%9D%A2%E5%9B%BEv1.png" alt="封面图" width="800" style="display: block; margin-left: auto; margin-right: auto;">


为了突破这些局限，「知络医诊」设计并实现了一款由**文心大模型**驱动的智能激光针灸机器人，旨在通过将先进的激光控制技术与智能诊疗决策系统相结合，实现个性化、自动化的家庭健康管理和慢性病防治。项目设计理念依托中医“治未病”理论，通过引入激光针灸和现代计算机视觉技术，实现从穴位精准识别到个性化激光治疗的完整闭环，提供全新的中医健康管理解决方案。

该项目的意义在于：
- 为家庭健康管理提供创新性的中医理疗解决方案，打破传统针灸的技术与应用壁垒；
- 提升中医针灸在现代医学中的应用水平，推动中医药的智能化和标准化发展；
- 为“健康中国2030”规划中提出的“治未病”理念提供技术支撑，实现中医治疗的普及化与现代化。

# 市场分析与需求调研

## 市场需求分析

随着全球人口老龄化和慢性病发病率的逐年上升，个人健康管理和慢病康复需求日益增长。特别是在家庭和基层医疗场景中，用户希望拥有能够自主操作、安全可靠的健康管理设备。而传统针灸疗法由于需要专业人员操作且治疗时间较长，无法满足家庭用户在便捷性与实用性上的要求。因此，具有自动化和个性化功能的激光针灸设备在这一领域存在显著的市场潜力。

激光针灸技术相较于传统针灸更易操作、无创且风险低，可以有效解决传统针灸中治疗过程繁琐、穴位定位难度大、治疗过程中可能引发感染等问题，特别适合慢性病患者、老年人及亚健康人群的日常健康管理和康复治疗。根据市场调研，全球激光医疗器械市场正以每年约10%的速度增长[[来源]](https://www.bosidata.com/news/167198TDHU.html)，而激光针灸设备作为其中的新兴细分市场，具有广阔的市场空间。

## 项目定位

目前市场上的激光针灸设备主要用于专业医疗机构，价格高且缺乏个性化，难以满足家庭用户需求。相比之下，「知络医诊」的优势在于：

1. **个性化治疗方案**：依托大模型的智能诊疗能力，根据用户体质、病情和症状生成定制化的针灸方案，提升治疗效果。
   
2. **精准穴位定位与自适应治疗**：采用计算机视觉技术识别穴位，并结合患者反馈动态调整激光参数，确保治疗的精确性和安全性。
   
3. **便捷易用**：设计简单易操作，普通用户经过培训即可使用。系统集成多种安全机制，确保家庭环境下的使用安全。

4. **高性价比**：通过模块化设计降低成本，并结合云端数据与边缘计算，实现高效、便捷的家庭健康管理。

「知络医诊」将中医理念与现代科技相结合，提供智能诊疗、精准治疗和健康管理一体化的解决方案，填补了家庭激光针灸市场的空白。

# 作品内容


## 功能架构图与流程概述

「知络医诊」基于“智能诊疗-视觉识别-精密治疗”三大核心模块构建了完整的激光针灸机器人诊疗系统：
<figure style="margin: 0; text-align: center;">
    <img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/02-%E6%9E%B6%E6%9E%84%E5%9B%BE.png" alt="架构图"  width="600" style="display: block; margin-left: auto; margin-right: auto;"> 
    <figcaption style="font-style: italic;">「知络医诊」系统架构图</figcaption>
</figure>

首先，智能诊疗模块通过文心大模型实现对用户的中医问诊和个性化针灸处方生成，为每位用户量身定制治疗方案。随后，视觉识别模块通过深度学习模型实时检测并定位用户体表的目标穴位，确保治疗方案能够精准实施。最后，精密激光治疗模块利用高精度激光控制系统，根据生成的针灸处方信息自动调整激光参数，模拟中医“捻转补泻”手法，完成个性化的治疗操作。各模块间通过数据流与控制流的实时交互形成闭环，从而实现诊断、定位到治疗的一体化中医针灸治疗流程。



---



## 平台功能与技术框架

本平台采用前后端分离的设计，前端基于Vue.js构建，实现动态响应的用户交互界面，便于用户轻松浏览和操作不同功能模块。后端采用SpringBoot框架进行业务逻辑的管理和API接口服务，确保平台的高稳定性和数据安全性。为了提升系统整体的用户体验，平台在数据交互中引入了WebSocket协议，实现问诊和治疗过程中数据的实时传输与显示。

在数据安全方面，「知络医诊」对所有用户隐私信息进行AES加密处理，并在问诊环节中进行脱敏操作，确保传输至智能诊疗模块的所有数据均为安全处理后的信息。用户的体质与病情数据只有经过脱敏保护后，才会被大模型处理与分析，以此规避潜在的数据泄露风险。此外，为提升数据隐私保护能力，平台的穴位识别模块采用边缘计算方案，部署在NVIDIA Jetson Nano设备上，直接在本地完成图像数据处理，减少数据外传风险，从而在提升响应速度的同时有效保护用户隐私。

---

## 由文心驱动的中医证型辨析和个性化针灸处方生成

该模块基于百度文心大模型及其强大的自然语言理解能力，结合团队自主构建的**中医针灸知识图谱**，能够在诊疗过程中像一位老中医一样，为用户提供精准的中医辨证论治针灸服务。



<div style="display: flex; align-items: flex-start;">

  <!-- 左侧图片 -->
  <figure style="margin: 0 20px 0 0; text-align: center;">
    <img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/03-%E9%97%AE%E8%AF%8A%E8%BF%87%E7%A8%8B%E7%A4%BA%E4%BE%8B.png" style="height: 300px;"/>
    <figcaption style="font-style: italic;">问诊过程示例（糖尿病）</figcaption>
  </figure>

  <!-- 右侧图片 -->
  <figure style="margin: 0; text-align: center;">
    <img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/04-%E9%92%88%E7%81%B8%E5%A4%84%E6%96%B9%E5%8D%A1%E7%89%87.png" style="height: 300px;"/>
    <figcaption style="font-style: italic;">「知络医诊」<br>生成的个性化针灸处方</figcaption>
  </figure>
  
</div>


首先，文心大模型通过对用户输入的症状描述和体质特征进行语义理解，判断其主诉病因，并自动匹配针灸知识图谱中记录的中医理论（包括病因病机、经络理论、穴位配伍）。随后，模型运用“辨证论治”理论进行动态推理，并根据患者的具体情况（如体质类型、病症发展程度等），准确辨析其证型类别（如气虚证、阴虚证等），生成个性化的针灸治疗方案，包括主要治疗穴位和配伍方案。文心大模型通过多轮问诊技术（基于思维链CoT构建）逐步深入挖掘用户症状，确保诊疗结果符合中医理论和个体化需求。

<div style="width:100%; height:600px; overflow:auto; border:1px solid lightgray;">
    <img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/04-%E9%92%88%E7%81%B8%E5%A4%84%E6%96%B9%E5%8D%A1%E7%89%87.png" style="width:100%;" />
</div>


---

## 智能激光治疗模块

<div style="display: flex; align-items: flex-start;">

  <!-- 左侧图片 -->
  <figure style="margin: 0 20px 0 0; text-align: center;">
    <img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/05-%E4%BA%8C%E7%BB%B4%E6%8C%AF%E9%95%9C%E7%BB%93%E6%9E%84%E7%A4%BA%E6%84%8F.jpg" style="height: 300px;"/>
    <figcaption style="font-style: italic;">激光控制机构原理示意</figcaption>
  </figure>

  <!-- 右侧图片 -->
  <figure style="margin: 0; text-align: center;">
    <img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/06-%E7%A1%AC%E4%BB%B6%E7%B3%BB%E7%BB%9F%E5%B1%95%E7%A4%BA.jpg" style="height: 300px;"/>
    <figcaption style="font-style: italic;">（原型）硬件系统展示</figcaption>
  </figure>
  
</div>

激光治疗模块基于二维振镜系统控制激光束的运动轨迹和照射参数，能够灵活地模拟传统针灸中的“捻转补泻”手法。系统通过调节激光的输出频率与照射强度，实现中医“补法”（低频长时刺激）与“泻法”（高频短时刺激）的效果，并能够根据不同穴位的治疗需求调整激光束的照射时间与能量，提供丰富的治疗手法选择。

<div style="display: flex; align-items: center; justify-content: center;">

  <!-- 左侧图片 -->
  <figure style="margin: 0 20px 0 0; text-align: center;">
    <img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/07-%E8%A1%A5%E6%B3%BB%E6%89%8B%E6%B3%95.jpg" style="height: 300px;"/>
    <figcaption style="font-style: italic;">针灸中的不同治疗手法（补法、泻法）</figcaption>
  </figure>

  <!-- 右侧视频 -->
  <figure style="margin: 0; text-align: center;">
    <video src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/08-%E5%A4%9A%E7%82%B9%E7%85%A7%E5%B0%84%E6%BC%94%E7%A4%BA%E8%A7%86%E9%A2%91.mp4" style="height: 300px;" autoplay loop muted></video>
    <figcaption style="font-style: italic;">多点同时跟踪治疗效果</figcaption>
  </figure>

</div>

此外，系统支持多穴位同时治疗，能够精确控制激光在多个穴位间快速切换，满足复杂针灸治疗方案的需求，从而在无创的条件下实现对多穴位的精准刺激与调理。

---



## 基于`PaddleDetection`的轻量化视觉穴位定位

<img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/09-tinypose.png" alt="tingpose"  width="600" style="display: block; margin-left: auto; margin-right: auto;">

视觉穴位定位模块采用迁移学习策略，利用公开手部关键点数据集（HandPose-v2）进行基础预训练，并基于针灸穴位数据集进行专有微调，以提升模型对不同体表特征的适应性。穴位定位采用二阶段Top-Down检测策略，首先使用PicoDet模型检测用户整体手部或目标区域，识别目标候选区域的包围框。然后在目标区域内使用PP-TinyPose模型进行细粒度穴位识别和关键点定位，确保复杂场景下的高精度穴位检测。


目前，我们已成功构建并部署了基于 `Top-Down` 策略的手部穴位检测模型，能够精准识别手部 **18 个常用穴位** ，包括手三阴经（肺经、心包经、心经）和手三阳经（大肠经、三焦经、小肠经）上主要的经穴，同时涵盖了一些常用的经外奇穴（如八邪穴）。通过对手部穴位的精准识别奠定了后续复杂穴位检测模块的开发基础。 

<img src="https://cccc-ai-2024.bj.bcebos.com/%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3/10-%E6%89%8B%E9%83%A8%E7%A9%B4%E4%BD%8D.png" alt="手部穴位"  width="600" style="display: block; margin-left: auto; margin-right: auto;">

该模型部署在NVIDIA Jetson Nano平台上，并经过 `PaddleLite` 量化与加速处理，使其能够在边缘设备上实现高效、实时的穴位识别，确保治疗过程中对穴位定位的精准性与稳定性。

--- 


```python

```
