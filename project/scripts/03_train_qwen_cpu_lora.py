import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model

# CPU-friendly Qwen model for Codespace demo training
MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")

TRAIN_FILE = "data/training/cve_instruction_train.jsonl"
OUTPUT_DIR = "adapters/qwen_codespace_cve_lora_adapter"

MAX_RECORDS = 100
MAX_LENGTH = 256


def format_example(example):
    return f"""### Instruction:
{example["instruction"]}

### Input:
{example["input"]}

### Response:
{example["output"]}"""


def main():
    print("CUDA available:", torch.cuda.is_available())
    print("Training mode: CPU-only Codespace demo")

    dataset = load_dataset("json", data_files=TRAIN_FILE, split="train")

    # Keep it small for CPU training
    dataset = dataset.select(range(min(MAX_RECORDS, len(dataset))))
    dataset = dataset.train_test_split(test_size=0.1, seed=42)

    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]

    print("Train examples:", len(train_dataset))
    print("Eval examples:", len(eval_dataset))

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        trust_remote_code=True
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,
        trust_remote_code=True
    )

    model.config.use_cache = False

    # Freeze base model
    for param in model.parameters():
        param.requires_grad = False

    # Add LoRA adapter
    lora_config = LoraConfig(
        r=4,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    def tokenize_function(example):
        text = format_example(example)

        tokenized = tokenizer(
            text,
            truncation=True,
            max_length=MAX_LENGTH,
            padding=False
        )

        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    tokenized_train = train_dataset.map(
        tokenize_function,
        remove_columns=train_dataset.column_names
    )

    tokenized_eval = eval_dataset.map(
        tokenize_function,
        remove_columns=eval_dataset.column_names
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=1,
        logging_steps=5,
        save_steps=25,
        save_total_limit=1,
        report_to="none",
        # `no_cuda` removed in newer transformers; rely on environment/torch
        # to select CPU/GPU automatically. For CPU-only runs ensure CUDA
        # isn't available or set CUDA_VISIBLE_DEVICES="" externally.
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        data_collator=data_collator
    )

    trainer.train()

    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"LoRA adapter saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()