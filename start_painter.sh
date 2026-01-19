#!/bin/bash
echo "🚀 LAUNCHING PAINTER..."

# Define paths
SD_REPO="$HOME/stable-diffusion-webui/repositories/stable-diffusion-stability-ai"
TAMING_REPO="$HOME/stable-diffusion-webui/repositories/taming-transformers"

# Setup Environment (Injects the missing modules)
export STABLE_DIFFUSION_COMMIT_HASH="HEAD"
export PYTHONPATH="$SD_REPO:$TAMING_REPO:$PYTHONPATH"

# Launch
cd ~/stable-diffusion-webui
./webui.sh --api --listen --skip-torch-cuda-test
