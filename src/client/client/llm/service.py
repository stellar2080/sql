import os
import sys
from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModelForCausalLM
import uvicorn
import json
import torch
current_dir = os.path.dirname(os.path.abspath(__file__))
CLIENT_PATH = os.path.dirname(current_dir)
sys.path.append(CLIENT_PATH)

# from modelscope import snapshot_download
# model_dir = snapshot_download('Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4', cache_dir='/home/stellar/model', revision='master') 

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE

def torch_gc():
    if torch.cuda.is_available():  
        with torch.cuda.device(CUDA_DEVICE):  
            torch.cuda.empty_cache()  
            torch.cuda.ipc_collect() 

app = FastAPI()
@app.post("/")
async def create_item(request: Request):
    global model, tokenizer  
    json_post_raw = await request.json()  
    json_post = json.dumps(json_post_raw)  
    json_post_list = json.loads(json_post)  
    messages = json_post_list.get('messages')  
    DO_SAMPLE = json_post_list.get('DO_SAMPLE')
    TEMPERATURE = json_post_list.get('TEMPERATURE')
    TOP_K = json_post_list.get('TOP_K')
    TOP_P = json_post_list.get('TOP_P')
    MAX_LENGTH = json_post_list.get('MAX_LENGTH')

    text = tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        input_ids=model_inputs.input_ids,
        max_length=MAX_LENGTH,
        do_sample=DO_SAMPLE,
        temperature=TEMPERATURE,
        top_k=TOP_K,
        top_p=TOP_P
    ) 
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    answer = {
        "response": response,
        "status": 200
    }
    torch_gc()  
    return answer  

if __name__ == '__main__':
    LLM_HOST = 'localhost'
    LLM_PORT = 6006
    model_path = '/home/stellar/model/LLM-Research/Meta-Llama-3___1-8B-Instruct-bnb-4bit'
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, device_map=CUDA_DEVICE, torch_dtype="auto", trust_remote_code=True).eval()
    uvicorn.run(app, host=LLM_HOST, port=LLM_PORT, workers=1)
