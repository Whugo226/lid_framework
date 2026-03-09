import torch

def check_gpu():
    print("--- PyTorch GPU Check ---")
    
    # 1. Is CUDA even available?
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        # 2. What is the name of the GPU?
        device_name = torch.cuda.get_device_name(0)
        print(f"GPU Detected:   {device_name}")
        
        # 3. How much VRAM does it have?
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"Total VRAM:     {total_memory:.2f} GB")
    else:
        print("\n❌ PyTorch is NOT seeing your GPU. It is defaulting to the CPU.")

if __name__ == "__main__":
    check_gpu()