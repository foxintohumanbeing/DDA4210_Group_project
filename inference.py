import torch
import json
import os
import diffusers
from diffusers import AutoencoderKL, DDPMScheduler, StableDiffusionPipeline, UNet2DConditionModel

def load_config(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

def main(config):
    # Load the trained pipeline
    pipeline = StableDiffusionPipeline.from_pretrained(
        config["pretrained_model_name_or_path"], revision=config["revision"], torch_dtype=torch.float32
    )
    pipeline = pipeline.to(config["device"])

    # Load attention processors
    pipeline.unet.load_attn_procs(config["output_dir"])

    # Set the generator for random number generation
    generator = torch.Generator(device=config["device"]).manual_seed(config["seed"])

    for prompt in config["prompts"]:
        # Generate images for the given prompt
        images = []
        for i in range(config["num_images"]):
            images.append(pipeline(prompt, num_inference_steps=30, generator=generator).images[0])

        # Save the generated images to the output directory
        prompt_output_dir = os.path.join(config["output_dir"], prompt.replace(" ", "_"))
        os.makedirs(prompt_output_dir, exist_ok=True)
        for i, image in enumerate(images):
            image.save(os.path.join(prompt_output_dir, f"image_{i}.png"))

if __name__ == "__main__":
    config_path = "config_test.json"
    config = load_config(config_path)
    main(config)
