set -e
cd ../LLaMA-Factory

# 修改以下路径
MODEL_PATH="/home/zmwang/public/public_data/models/Qwen2.5-VL-7B-Instruct"  # 基础模型路径
OUTPUT_PATH="/home/zmwang/storage/codes/LLaMA-Factory/results/Qwen2.5-VL-7B-Instruct_lora_ir262144_dsalpaca_en_demo_ct16384_lr1d0e-5_pbs1_g1_e3d0"  # LoRA微调输出路径
merge_output_path="/home/aiseon/storage/zmwang_data/codes/LLaMA-Factory/results"  # 合并后模型保存路径


export CUDA_VISIBLE_DEVICES="3"

# 执行合并
sed -e "s|{model_path}|$MODEL_PATH|" \
    -e "s|{adapter_path}|$OUTPUT_PATH|" \
    -e "s|{output_path}|$merge_output_path|" \
    ../embodied_reasoner/finetune/lora/merge_lora/template.yaml > ./examples/merge_lora/qwen2_vl_lora_merge.yaml

llamafactory-cli export ./examples/merge_lora/qwen2_vl_lora_merge.yaml