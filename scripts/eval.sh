MODEL_PATH=$1
MODEL_NAME=$2

# image_resolution
export IMAGE_RESOLUTION=351232
export MIN_PIXELS=3136
export MAX_PIXELS=351232
MODEL_TYPE="qwen2_vl"
# MODEL_TYPE="qwen2_5_vl"
export PYTHONUNBUFFERED=1
# export NCCL_P2P_DISABLE=1

# embedding model for match object
python ./inference/local_deploy.py \
    --embedding 1 \
    --port 20000

# vison language model inference server
CUDA_VISIBLE_DEVICES=1 python inference/local_deploy.py \
    --frame "hf" \
    --model_type $MODEL_TYPE \
    --model_name $MODEL_PATH \
    --port 10001

wait

# start ai2thor engine and request inference server
CUDA_VISIBLE_DEVICES=0 python evaluate/evaluate.py \
        --model_name $MODEL_NAME \
        --input_path "data/test_809.json" \
        --batch_size 200 \
        --cur_count 1 \
        --port 10001 \
        --total_count 1

wait 

python evaluate/showresult.py \
    --model_name $MODEL_NAME