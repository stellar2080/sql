import os
import sys
from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import uvicorn
import json
import torch
current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(current_dir)
sys.path.append(ROOT_PATH)
from src.utils.const import MAX_TOKENS, TEMPERATURE, LLM_HOST, LLM_PORT

# from modelscope import snapshot_download
# model_dir = snapshot_download('Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4', cache_dir='/home/stellar/model', revision='master') 

# 设置设备参数
DEVICE = "cuda"  # 使用CUDA
DEVICE_ID = "0"  # CUDA设备ID，如果未设置则为空
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE  # 组合CUDA设备信息

# 清理GPU内存函数
def torch_gc():
    if torch.cuda.is_available():  # 检查是否可用CUDA
        with torch.cuda.device(CUDA_DEVICE):  # 指定CUDA设备
            torch.cuda.empty_cache()  # 清空CUDA缓存
            torch.cuda.ipc_collect()  # 收集CUDA内存碎片

# 创建FastAPI应用
app = FastAPI()
@app.post("/")
async def create_item(request: Request):
    global model, tokenizer  # 声明全局变量以便在函数内部使用模型和分词器
    json_post_raw = await request.json()  # 获取POST请求的JSON数据
    json_post = json.dumps(json_post_raw)  # 将JSON数据转换为字符串
    json_post_list = json.loads(json_post)  # 将字符串转换为Python对象
    messages = json_post_list.get('messages')  # 获取请求中的提示

    # 调用模型进行对话生成
    text = tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(model_inputs.input_ids,temperature=TEMPERATURE,max_new_tokens=MAX_TOKENS) # 思考需要输出更多的Token数，设为8K
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # 构建响应JSON
    answer = {
        "response": response,
        "status": 200
    }
    torch_gc()  # 执行GPU内存清理
    return answer  # 返回响应

# 主函数入口
if __name__ == '__main__':
    # 加载预训练的分词器和模型
    model_path = '/home/stellar/model/LLM-Research/Meta-Llama-3.1-8B-Instruct-bnb-4bit'
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, device_map=CUDA_DEVICE, torch_dtype="auto", trust_remote_code=True).eval()
    uvicorn.run(app, host=LLM_HOST, port=LLM_PORT, workers=1)
