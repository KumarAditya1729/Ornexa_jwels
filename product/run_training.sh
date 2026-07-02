#!/bin/bash
export MODEL_NAME="runwayml/stable-diffusion-v1-5"
export DATASET_DIR="./data/lora_training"
export OUTPUT_DIR="./model_output/ornexa_bangle_lora"

echo "[Training] Starting LoRA Fine-Tuning on $DATASET_DIR..."

# We use very aggressive optimization settings for Mac MPS (Apple Silicon)
# - train_batch_size=1 (to fit in Unified Memory)
# - gradient_accumulation_steps=4 (to simulate a batch size of 4)
# - max_train_steps=100 (Since this is just a micro-dataset test to verify math)
# - mixed_precision="no" (MPS sometimes struggles with fp16 in older diffusers training scripts)

source ingestion/venv/bin/activate
accelerate launch --mixed_precision="no" product/train_text_to_image_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --train_data_dir=$DATASET_DIR \
  --dataloader_num_workers=0 \
  --resolution=512 \
  --center_crop \
  --random_flip \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --max_train_steps=100 \
  --learning_rate=1e-04 \
  --max_grad_norm=1 \
  --lr_scheduler="cosine" \
  --lr_warmup_steps=0 \
  --output_dir=${OUTPUT_DIR} \
  --checkpointing_steps=500 \
  --validation_prompt="A highly detailed, intricate gold jewelry bracelet, professional photography, white background" \
  --seed=1337

echo "[Training] Complete! LoRA weights saved to $OUTPUT_DIR"
