from mcp.server.fastmcp import FastMCP

mcp = FastMCP("好孕安安_核心算法组")

# ================= 工具 1：B超测算 =================
@mcp.tool()
def calculate_fetal_weight(bpd: float, ac: float, fl: float) -> str:
    """
    当孕妇提供B超单数据时调用，计算胎儿预估体重 (EFW)。
    参数:
    - bpd: 双顶径 (毫米)
    - ac: 腹围 (毫米)
    - fl: 股骨长 (毫米)
    """
    weight = 1.07 * (bpd ** 3) + 0.3 * ac * fl
    
    if weight > 2500:
        status = "预估偏大，触发预警，请建议孕妈妈控制精制碳水摄入。"
    elif weight < 1500:
        status = "预估偏小，建议多补充高蛋白食物。"
    else:
        status = "发育指标完美，符合当前孕周！"
        
    return f"【MCP云端测算结果】胎儿预估体重: {weight:.2f}g。干预策略: {status}"

# ================= 工具 2：糖耐量评估 =================
@mcp.tool()
def analyze_ogtt_risk(fasting: float, one_hour: float, two_hour: float) -> str:
    """
    当孕妇提供糖耐量(OGTT)检查结果时调用，评估妊娠期糖尿病风险。
    参数:
    - fasting: 空腹血糖值 (mmol/L)
    - one_hour: 喝糖水后1小时血糖值 (mmol/L)
    - two_hour: 喝糖水后2小时血糖值 (mmol/L)
    """
    abnormal_count = 0
    details = []
    if fasting >= 5.1:
        abnormal_count += 1
        details.append(f"空腹 {fasting}")
    if one_hour >= 10.0:
        abnormal_count += 1
        details.append(f"1小时 {one_hour}")
    if two_hour >= 8.5:
        abnormal_count += 1
        details.append(f"2小时 {two_hour}")
        
    if abnormal_count > 0:
        return f"【MCP云端测算结果】检测到 {abnormal_count} 项超标 ({', '.join(details)})。存在妊娠期糖尿病风险，请立刻联动知识库生成控糖食谱！"
    else:
        return "【MCP云端测算结果】OGTT三项指标均在安全范围内，糖代谢功能良好！"

# ================= 工具 3：BMI追踪 =================
@mcp.tool()
def evaluate_weight_trajectory(height_cm: float, pre_weight_kg: float, current_week: int, current_weight_kg: float) -> str:
    """
    根据孕前BMI和当前孕周，评估孕妈妈体重增长是否合理。
    参数:
    - height_cm: 身高(厘米)
    - pre_weight_kg: 孕前体重(公斤)
    - current_week: 当前孕周
    - current_weight_kg: 当前体重(公斤)
    """
    height_m = height_cm / 100
    bmi = pre_weight_kg / (height_m ** 2)
    gain = current_weight_kg - pre_weight_kg
    
    return f"【MCP云端测算结果】孕前BMI: {bmi:.1f}。已增重: {gain:.1f}kg。当前处于第{current_week}周，请结合知识库指导营养摄入。"

# 🚨 极其关键：启动命令必须放在最后面！系统才会把上面的工具全读完 🚨
# 🚨 专门适配 Render 的云端启动命令 🚨
if __name__ == "__main__":
    import os
    import uvicorn
    # 获取 Render 动态分配的端口，默认 8000
    port = int(os.environ.get("PORT", 8000))
    # 提取 FastMCP 的底层 ASGI 接口并运行
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=port)