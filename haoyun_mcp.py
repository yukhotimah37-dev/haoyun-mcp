from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn
import os

# 1. 拆分成三个完全独立的 MCP 服务器
mcp_fetal = FastMCP("B超测算")
mcp_ogtt = FastMCP("糖耐量评估")
mcp_weight = FastMCP("体重追踪")

# ================= 工具 1 =================
@mcp_fetal.tool()
def calculate_fetal_weight(bpd: float, ac: float, fl: float) -> str:
    weight = 1.07 * (bpd ** 3) + 0.3 * ac * fl
    if weight > 2500:
        status = "预估偏大，触发预警，请建议孕妈妈控制精制碳水摄入。"
    elif weight < 1500:
        status = "预估偏小，建议多补充高蛋白食物。"
    else:
        status = "发育指标完美，符合当前孕周！"
    return f"【MCP云端测算结果】胎儿预估体重: {weight:.2f}g。干预策略: {status}"

# ================= 工具 2 =================
@mcp_ogtt.tool()
def analyze_ogtt_risk(fasting: float, one_hour: float, two_hour: float) -> str:
    abnormal_count = 0
    details = []
    if fasting >= 5.1: abnormal_count += 1; details.append(f"空腹 {fasting}")
    if one_hour >= 10.0: abnormal_count += 1; details.append(f"1小时 {one_hour}")
    if two_hour >= 8.5: abnormal_count += 1; details.append(f"2小时 {two_hour}")
    if abnormal_count > 0:
        return f"【MCP云端测算结果】检测到 {abnormal_count} 项超标 ({', '.join(details)})。存在妊娠期糖尿病风险，请立刻联动知识库生成控糖食谱！"
    else:
        return "【MCP云端测算结果】OGTT三项指标均在安全范围内，糖代谢功能良好！"

# ================= 工具 3 =================
@mcp_weight.tool()
def evaluate_weight_trajectory(height_cm: float, pre_weight_kg: float, current_week: int, current_weight_kg: float) -> str:
    height_m = height_cm / 100
    bmi = pre_weight_kg / (height_m ** 2)
    gain = current_weight_kg - pre_weight_kg
    return f"【MCP云端测算结果】孕前BMI: {bmi:.1f}。已增重: {gain:.1f}kg。当前处于第{current_week}周，请结合知识库指导营养摄入。"

# 2. 核心：给它们分配三个独立的专属网址
app = Starlette(
    routes=[
        Mount("/fetal", mcp_fetal.sse_app()),
        Mount("/ogtt", mcp_ogtt.sse_app()),
        Mount("/weight", mcp_weight.sse_app()),
    ]
)

# 3. 专门适配 Render 的云端启动命令
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)