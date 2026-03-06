# Training Configuration

## Hyperparameter Defaults

### For Supervised Fine-Tuning (SFT)

| Parameter | Default | Range | Notes |
|-----------|---------|-------|-------|
| Learning rate | 2e-4 | 1e-5 to 5e-4 | Lower for larger models |
| Epochs | 1-3 | 1-5 | More = overfitting risk |
| Batch size | 4-8 | 2-32 | Higher = more stable, more VRAM |
| Warmup ratio | 0.03 | 0.01-0.1 | 3% of total steps |
| Weight decay | 0.01 | 0-0.1 | Regularization |

### For LoRA/QLoRA

| Parameter | Default | Notes |
|-----------|---------|-------|
| Rank (r) | 16 | 8-64, higher = more capacity |
| Alpha | 16 | Usually equals rank |
| Dropout | 0 | 0-0.1, use if overfitting |
| Target modules | All attention | q, k, v, o, gate, up, down proj |

### For RLHF/DPO/GRPO

| Parameter | Default | Notes |
|-----------|---------|-------|
| Learning rate | 5e-6 | 10-50x lower than SFT |
| Beta (DPO) | 0.1 | Controls preference strength |
| Epochs | 1 | Usually single pass |

## Training with Unsloth (Recommended)

```python
from unsloth import FastLanguageModel

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B",
    max_seq_length=2048,
    load_in_4bit=True,  # QLoRA
)

# Apply LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", 
                    "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    use_gradient_checkpointing="unsloth",
)

# Train
from trl import SFTTrainer

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=100,
        learning_rate=2e-4,
        output_dir="outputs",
    ),
)

trainer.train()
```

## Training with OpenAI

```python
from openai import OpenAI
client = OpenAI()

# Upload file
file = client.files.create(
    file=open("training.jsonl", "rb"),
    purpose="fine-tune"
)

# Create job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": 3,
        "learning_rate_multiplier": 1.0,  # 0.1-2.0
        "batch_size": 4,
    }
)

# Monitor
while True:
    job = client.fine_tuning.jobs.retrieve(job.id)
    print(f"Status: {job.status}")
    if job.status in ["succeeded", "failed"]:
        break
    time.sleep(60)
```

## Monitoring Training

### Key Metrics to Watch

| Metric | Healthy | Problem |
|--------|---------|---------|
| Training loss | Decreasing smoothly | Jumping, not decreasing |
| Validation loss | Decreasing, then stable | Increasing = overfitting |
| Gradient norm | Stable, <10 | Exploding (>100) or vanishing (<0.001) |
| Learning rate | Following schedule | N/A |

### Overfitting Signals

1. Training loss continues dropping while val loss increases
2. Model memorizes training examples verbatim
3. Performance on held-out test set degrades

### Fixes for Overfitting

- Reduce epochs (try 1-2 instead of 3+)
- Add dropout (0.05-0.1)
- Reduce learning rate
- Add more training data
- Early stopping based on val loss

## Preventing Catastrophic Forgetting

Problem: Model loses general capabilities while learning specific task.

Solutions:
1. **Mix general data** — Include 20% general instruction data in training mix
2. **Lower learning rate** — Slow learning preserves base knowledge
3. **Regularization** — Weight decay, dropout
4. **Elastic Weight Consolidation** — Advanced technique for critical params

```python
# Example: mixing task-specific with general data
mixed_dataset = concatenate_datasets([
    task_specific_data,  # 80%
    general_instructions_data.select(range(len(task_specific_data) // 4))  # 20%
])
```
