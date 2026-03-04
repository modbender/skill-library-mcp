import requests
import json

def send_message(user_id, text):
    url = "http://127.0.0.1:51200/ask"
    payload = {
        "user_id": user_id,
        "text": text
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # requests 会自动处理编码，不需要担心 ascii 报错
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # 如果状态码不是 200，会抛出异常
        
        result = response.json()
        #print(f"\n[Agent]: {result.get('response')}")
        print(f"\n[Agent]: {result}")
    except Exception as e:
        print(f"\n[Error]: {e}")

if __name__ == "__main__":
    print("=== Xavier Agent Python 测试客户端 ===")
    print("(输入 'exit' 退出对话)")
    
    uid = "Xavier_01"
    
    while True:
        user_input = input("\n[You]: ")
        if user_input.lower() == 'exit':
            break
        if not user_input.strip():
            continue
            
        send_message(uid, user_input)
# import httpx
# import asyncio
# import json

# SCHEDULER_URL = "http://127.0.0.1:51201/tasks"

# async def run_test():
#     async with httpx.AsyncClient() as client:
#         # --- 1. 定一个 1:00 的闹钟 ---
#         # print("\n--- 步骤 1: 增加定时任务 ---")
#         # task_data = {
#         #     "user_id": "Xavier_01",
#         #     "cron": "0 1 * * *",  # 凌晨 1 点
#         #     "text": "系统巡检：请分析最近的对话压力。"
#         # }
#         # resp_add = await client.post(SCHEDULER_URL, json=task_data)
#         # if resp_add.status_code == 200:
#         #     task_id = resp_add.json()["task_id"]
#         #     print(f"✅ 增加成功！分配的 ID: {task_id}")
#         # else:
#         #     print(f"❌ 增加失败: {resp_add.text}")
#         #     return

#         # # --- 2. 查看定时列表 ---
#         # print("\n--- 步骤 2: 查看所有任务 ---")
#         # resp_list = await client.get(SCHEDULER_URL)
#         # tasks = resp_list.json()
#         # print(f"当前共有 {len(tasks)} 个任务:")
#         # for t in tasks:
#         #     print(f"- ID: {t['task_id']}, 时间: {t['cron']}, 指令: {t['text']}")

#         # # --- 3. 删除刚才定的闹钟 ---
#         # print(f"\n--- 步骤 3: 删除任务 {task_id} ---")
#         # resp_del = await client.delete(f"{SCHEDULER_URL}/{task_id}")
#         # if resp_del.status_code == 200:
#         #     print(f"✅ 删除成功: {resp_del.json()}")
#         # else:
#         #     print(f"❌ 删除失败: {resp_del.text}")

#         # --- 4. 再次查看验证 ---
#         print("\n--- 步骤 4: 最终确认列表 ---")
#         resp_final = await client.get(SCHEDULER_URL)
#         print(f"剩余任务数量: {len(resp_final.json())}")

# if __name__ == "__main__":
#     asyncio.run(run_test())