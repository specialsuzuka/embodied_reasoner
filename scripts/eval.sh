# MODEL_PATH=$1
# MODEL_NAME=$2

# export PORT1=51001
# export PORT2=51002


MODEL_PATH=/home/aiseon/storage/zmwang_data/codes/LLaMA-Factory/results/Qwen2.5-VL-7B-Instruct-lora-finetuned-on-embodied-resoner
MODEL_NAME=Qwen2.5-VL-7B-Instruct

# image_resolution
export IMAGE_RESOLUTION=351232
export MIN_PIXELS=3136
export MAX_PIXELS=351232
# MODEL_TYPE="qwen2_vl"
MODEL_TYPE="qwen2_5_vl"
export PYTHONUNBUFFERED=1
# export NCCL_P2P_DISABLE=1

# embedding model for match object
python ./inference/local_deploy.py \
    --embedding 1 \
    --port 7001 &

# vison language model inference server
CUDA_VISIBLE_DEVICES=1 python inference/local_deploy.py \
    --frame "hf" \
    --model_type $MODEL_TYPE \
    --model_name $MODEL_PATH \
    --port 7002 &

echo "Waiting for ports ..."
while ! nc -z localhost 7001; do   
  sleep 1
done

while ! nc -z localhost 7002; do   
  sleep 1
done

# start ai2thor engine and request inference server
# CUDA_VISIBLE_DEVICES=0 
python evaluate/evaluate.py \
        --model_name $MODEL_NAME \
        --input_path "data/test_809.json" \
        --batch_size 200 \
        --cur_count 1 \
        --port 7002 \
        --total_count 1

wait 

python evaluate/show_result.py \
    --model_name $MODEL_NAME