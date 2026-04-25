"""build_notebook.py — generates grpo_training.ipynb with T4-safe configs."""
import json, os

def cell(source, cell_type="code"):
    if cell_type == "markdown":
        return {"cell_type": "markdown", "metadata": {}, "source": [source]}
    return {"cell_type": "code", "metadata": {}, "source": [source],
            "execution_count": None, "outputs": []}

cells = []

# ── Markdown header ──
cells.append(cell(
    "# M&A Due Diligence RL Training — 3-Phase Pipeline\n\n"
    "| Phase | Purpose | ~Time on T4 |\n"
    "|-------|---------|-------------|\n"
    "| **1. SFT Warm-up** | Teach JSON output format | ~5 min |\n"
    "| **2. Lightweight GRPO** | Test full RL loop (10 steps) | ~10 min |\n"
    "| **3. Full GRPO** | Actual training → curves | ~45-90 min |\n\n"
    "> GPU: T4 (15 GB VRAM). Peak usage ~10 GB. `load_in_4bit=True` keeps it safe.",
    "markdown"
))

# ── Cell 1: Install ──
cells.append(cell(
    "# Cell 1: Install\n"
    "!pip install -q 'unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git'\n"
    "!pip install -q trl datasets httpx fastapi uvicorn slowapi matplotlib pydantic\n"
    "import torch\n"
    "print('CUDA available:', torch.cuda.is_available())\n"
    "print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU — switch runtime!')"
))

# ── Cell 2: Setup ──
cells.append(cell(
    "# Cell 2: Setup — clone repo and find project root\n"
    "import os, sys, glob\n\n"
    "# Uncomment ONE of these:\n"
    "# Option A: clone from GitHub\n"
    "# !git clone https://github.com/NJVinay/scaler-meta-hackathon.git\n\n"
    "# Option B: upload zip via Colab file panel, then:\n"
    "# import zipfile; zipfile.ZipFile('output.zip').extractall('.')\n\n"
    "# Auto-detect project root: find the directory that contains server/\n"
    "def find_project_root(start='.', max_depth=4):\n"
    "    # Check current dir first\n"
    "    if os.path.isdir(os.path.join(start, 'server')):\n"
    "        return os.path.abspath(start)\n"
    "    # Search subdirs\n"
    "    for depth in range(1, max_depth + 1):\n"
    "        pattern = os.path.join(start, *(['*'] * depth), 'server')\n"
    "        for match in glob.glob(pattern):\n"
    "            if os.path.isdir(match):\n"
    "                return os.path.abspath(os.path.dirname(match))\n"
    "    return os.path.abspath(start)\n\n"
    "PROJECT_ROOT = find_project_root()\n"
    "os.chdir(PROJECT_ROOT)\n"
    "sys.path.insert(0, PROJECT_ROOT)\n\n"
    "# Verify critical dirs exist\n"
    "for d in ['server', 'security', 'training']:\n"
    "    assert os.path.isdir(d), f'Missing {d}/ in {PROJECT_ROOT}'\n\n"
    "print(f'Project root: {PROJECT_ROOT}')\n"
    "print(f'Files: {sorted(os.listdir(\".\"))}')"
))

# ── Cell 3: Start server ──
cells.append(cell(
    "# Cell 3: Start environment server\n"
    "import subprocess, time, httpx, sys, tempfile, os\n\n"
    "# Capture stderr so server import errors are visible\n"
    "_server_log = os.path.join(tempfile.gettempdir(), 'ma_server.log')\n"
    "_server_logf = open(_server_log, 'w')\n\n"
    "# CRITICAL: pass cwd + PYTHONPATH so the subprocess can find server/\n"
    "_env = {**os.environ, 'PYTHONPATH': PROJECT_ROOT}\n"
    "server_proc = subprocess.Popen(\n"
    "    [sys.executable, '-m', 'uvicorn', 'server.app:app',\n"
    "     '--host', '0.0.0.0', '--port', '7860'],\n"
    "    stdout=_server_logf, stderr=_server_logf,\n"
    "    cwd=PROJECT_ROOT,\n"
    "    env=_env,\n"
    ")\n"
    "time.sleep(5)\n\n"
    "try:\n"
    "    r = httpx.get('http://localhost:7860/health', timeout=10)\n"
    "    assert r.status_code == 200\n"
    "    print('Server healthy:', r.json())\n"
    "except Exception as e:\n"
    "    _server_logf.flush()\n"
    "    print(f'Server failed to start: {e}')\n"
    "    print('--- Server log (last 50 lines) ---')\n"
    "    with open(_server_log) as f:\n"
    "        lines = f.readlines()\n"
    "        for line in lines[-50:]:\n"
    "            print(line, end='')\n"
    "    print('--- End server log ---')\n"
    "    raise"
))

# ── Cell 4: Load model ──
cells.append(cell(
    "# Cell 4: Load Qwen2.5-3B with Unsloth + LoRA\n"
    "from unsloth import FastLanguageModel\n\n"
    "model, tokenizer = FastLanguageModel.from_pretrained(\n"
    "    model_name='unsloth/Qwen2.5-3B-Instruct',\n"
    "    max_seq_length=2048,\n"
    "    load_in_4bit=True,   # ~2.5 GB VRAM on T4\n"
    "    dtype=None,\n"
    ")\n\n"
    "model = FastLanguageModel.get_peft_model(\n"
    "    model, r=16, lora_alpha=16,\n"
    "    target_modules=['q_proj','k_proj','v_proj','o_proj',\n"
    "                    'gate_proj','up_proj','down_proj'],\n"
    "    lora_dropout=0.0, bias='none',\n"
    "    use_gradient_checkpointing='unsloth',\n"
    "    random_state=42,\n"
    ")\n"
    "print('Model on device:', next(model.parameters()).device)\n"
    "print('LoRA applied successfully')"
))

# ── Markdown: Phase 1 ──
cells.append(cell("---\n## Phase 1: SFT Warm-up\nTeaches JSON format on 20 curated M&A examples.", "markdown"))

# ── Cell 5: SFT ──
cells.append(cell(
    "# Cell 5: SFT warm-up (T4-safe: batch=1, SFTConfig fallback)\n"
    "# SFTConfig requires trl>=0.8.0 — use TrainingArguments as safe fallback\n"
    "try:\n"
    "    from trl import SFTTrainer, SFTConfig as _SFTArgs\n"
    "    _sft_extra = dict(max_seq_length=2048, dataset_text_field='text')\n"
    "    _sft_trainer_extra = {}\n"
    "    print('Using SFTConfig')\n"
    "except ImportError:\n"
    "    from trl import SFTTrainer\n"
    "    from transformers import TrainingArguments as _SFTArgs\n"
    "    _sft_extra = {}\n"
    "    _sft_trainer_extra = dict(max_seq_length=2048, dataset_text_field='text')\n"
    "    print('Using TrainingArguments fallback')\n\n"
    "from datasets import Dataset\n"
    "from training.sft_data import SFT_EXAMPLES\n\n"
    "MA_SYSTEM_PROMPT = (\n"
    "    'You are an expert M&A due diligence analyst.\\n'\n"
    "    'You review NDAs, Letters of Intent, Share Purchase Agreements,\\n'\n"
    "    'and Representations & Warranties to identify risk clauses,\\n'\n"
    "    'quantify deal exposure, and rewrite unfavourable terms.\\n'\n"
    "    'Always respond in the JSON format specified in the task prompt.\\n'\n"
    "    'Reason from the document content - not from memorised templates.'\n"
    ")\n\n"
    "def format_prompt(task_prompt, deal_excerpt):\n"
    "    return (f'<|system|>\\n{MA_SYSTEM_PROMPT}\\n'\n"
    "            f'<|user|>\\n{task_prompt}\\n\\nDocument:\\n{deal_excerpt}\\n'\n"
    "            f'<|assistant|>\\n')\n\n"
    "def fmt_sft(ex):\n"
    "    return {'text': f'<|system|>\\n{MA_SYSTEM_PROMPT}\\n<|user|>\\n{ex[\"prompt\"]}\\n<|assistant|>\\n{ex[\"completion\"]}'}\n\n"
    "sft_dataset = Dataset.from_list(SFT_EXAMPLES).map(fmt_sft)\n\n"
    "sft_args = _SFTArgs(\n"
    "    output_dir='./sft-checkpoint',\n"
    "    num_train_epochs=3,\n"
    "    per_device_train_batch_size=1,  # T4 safe\n"
    "    gradient_accumulation_steps=4,\n"
    "    learning_rate=2e-4,\n"
    "    logging_steps=5,\n"
    "    save_steps=999,\n"
    "    report_to='none',\n"
    "    **_sft_extra,\n"
    ")\n\n"
    "sft_trainer = SFTTrainer(\n"
    "    model=model, tokenizer=tokenizer,\n"
    "    train_dataset=sft_dataset, args=sft_args,\n"
    "    **_sft_trainer_extra,\n"
    ")\n"
    "print(f'SFT: {len(sft_dataset)} examples x3 epochs')\n"
    "sft_trainer.train()\n"
    "sft_log = sft_trainer.state.log_history\n"
    "print('Phase 1 complete!')"
))

# ── Cell 6: Verify SFT ──
cells.append(cell(
    "# Cell 6: Verify SFT — check JSON compliance\n"
    "import json, torch\n"
    "from client import MADueDiligenceClient\n"
    "from models import Action\n\n"
    "env = MADueDiligenceClient(base_url='http://localhost:7860')\n"
    "FastLanguageModel.for_inference(model)\n\n"
    "json_ok = 0\n"
    "for i in range(5):\n"
    "    obs = env.reset(seed=i)\n"
    "    inputs = tokenizer(format_prompt(obs.task_prompt, obs.deal_excerpt),\n"
    "                       return_tensors='pt').to(model.device)\n"
    "    with torch.no_grad():\n"
    "        out = model.generate(**inputs, max_new_tokens=256,\n"
    "                             do_sample=True, temperature=0.7)\n"
    "    text = tokenizer.decode(out[0][inputs['input_ids'].shape[1]:],\n"
    "                            skip_special_tokens=True).strip()\n"
    "    try:\n"
    "        parsed = json.loads(text)\n"
    "        json_ok += 1\n"
    "        print(f'[{i}] OK keys={list(parsed.keys())}')\n"
    "    except json.JSONDecodeError:\n"
    "        print(f'[{i}] BAD: {text[:80]}')\n\n"
    "print(f'JSON compliance: {json_ok}/5')\n"
    "assert json_ok >= 2, 'Too few valid JSON outputs — re-run SFT with more epochs'\n"
    "FastLanguageModel.for_training(model)"
))

# ── Markdown: Phase 2 ──
cells.append(cell("---\n## Phase 2: Lightweight GRPO (10-step bug catcher)\nValidates the full loop before committing to a long run.", "markdown"))

# ── Cell 7: Reward function ──
cells.append(cell(
    "# Cell 7: Reward function\n"
    "import json, traceback\n\n"
    "def ma_reward_func(completions, **kwargs):\n"
    "    \"\"\"Called by GRPOTrainer. Sends each completion to the M&A env.\"\"\"\n"
    "    rewards = []\n"
    "    for completion in completions:\n"
    "        try:\n"
    "            text = completion if isinstance(completion, str) else str(completion)\n"
    "            if '<|assistant|>' in text:\n"
    "                text = text.split('<|assistant|>')[-1].strip()\n"
    "            # Auto-detect action type from JSON keys\n"
    "            action_type = 'identify'\n"
    "            try:\n"
    "                p = json.loads(text)\n"
    "                if 'risk_level' in p: action_type = 'assess'\n"
    "                elif 'rewritten_clause' in p: action_type = 'rewrite'\n"
    "            except Exception: pass\n"
    "            obs = env.reset()\n"
    "            obs2 = env.step(Action(agent_output=text, action_type=action_type))\n"
    "            rewards.append(float(obs2.reward or 0.0))\n"
    "        except Exception as e:\n"
    "            print(f'Reward error: {e}')\n"
    "            rewards.append(0.0)\n"
    "    return rewards\n\n"
    "print('Reward function ready')"
))

# ── Cell 8: Phase 2 GRPO test ──
cells.append(cell(
    "# Cell 8: Phase 2 — 10-step GRPO test\n"
    "from trl import GRPOConfig, GRPOTrainer\n"
    "from datasets import Dataset\n"
    "import inspect\n\n"
    "obs0 = env.reset(seed=0)\n"
    "test_dataset = Dataset.from_dict(\n"
    "    {'prompt': [format_prompt(obs0.task_prompt, obs0.deal_excerpt)] * 10}\n"
    ")\n\n"
    "test_cfg = GRPOConfig(\n"
    "    output_dir='./grpo-test',\n"
    "    max_steps=10,\n"
    "    learning_rate=5e-6,\n"
    "    per_device_train_batch_size=1,\n"
    "    gradient_accumulation_steps=2,\n"
    "    num_generations=2,\n"
    "    max_completion_length=256,\n"
    "    logging_steps=1,\n"
    "    report_to='none',\n"
    ")\n\n"
    "# TRL API varies across versions — detect the correct kwarg name\n"
    "_grpo_params = inspect.signature(GRPOTrainer.__init__).parameters\n"
    "_reward_kwargs = {}\n"
    "if 'reward_funcs' in _grpo_params:\n"
    "    _reward_kwargs['reward_funcs'] = [ma_reward_func]\n"
    "    print('TRL API: using reward_funcs (list)')\n"
    "elif 'reward_func' in _grpo_params:\n"
    "    _reward_kwargs['reward_func'] = ma_reward_func\n"
    "    print('TRL API: using reward_func (singular)')\n"
    "elif 'reward_fn' in _grpo_params:\n"
    "    _reward_kwargs['reward_fn'] = ma_reward_func\n"
    "    print('TRL API: using reward_fn')\n"
    "else:\n"
    "    # Fallback: try the most common\n"
    "    _reward_kwargs['reward_funcs'] = [ma_reward_func]\n"
    "    print('TRL API: defaulting to reward_funcs (list)')\n\n"
    "test_trainer = GRPOTrainer(\n"
    "    model=model, tokenizer=tokenizer,\n"
    "    train_dataset=test_dataset, args=test_cfg,\n"
    "    **_reward_kwargs,\n"
    ")\n"
    "print('Phase 2: 10-step test...')\n"
    "try:\n"
    "    test_trainer.train()\n"
    "    print('Phase 2 PASSED')\n"
    "    phase2_ok = True\n"
    "except Exception as e:\n"
    "    traceback.print_exc()\n"
    "    phase2_ok = False\n"
    "    print('Phase 2 FAILED — fix before Phase 3!')"
))

# ── Markdown: Phase 3 ──
cells.append(cell("---\n## Phase 3: Full GRPO Training\nOnly runs if Phase 2 passed. Produces reward + loss curves.", "markdown"))

# ── Cell 9: Full GRPO ──
cells.append(cell(
    "# Cell 9: Full GRPO\n"
    "assert phase2_ok, 'Phase 2 failed — fix bugs first!'\n\n"
    "# Build diverse prompts from actual environment\n"
    "full_prompts = []\n"
    "for i in range(200):\n"
    "    obs = env.reset(seed=i)\n"
    "    full_prompts.append(format_prompt(obs.task_prompt, obs.deal_excerpt))\n\n"
    "full_dataset = Dataset.from_dict({'prompt': full_prompts})\n\n"
    "# T4 note: grad_accum=8 (~45 min). Use 64 on A100 for better estimates.\n"
    "full_cfg = GRPOConfig(\n"
    "    output_dir='./ma-rl-checkpoints',\n"
    "    num_train_epochs=1,\n"
    "    learning_rate=5e-6,\n"
    "    per_device_train_batch_size=1,\n"
    "    gradient_accumulation_steps=8,\n"
    "    num_generations=4,\n"
    "    max_completion_length=256,\n"
    "    logging_steps=5,\n"
    "    save_steps=25,\n"
    "    report_to='none',\n"
    ")\n"
    "# Reuse the same reward kwarg detected in Phase 2\n"
    "full_trainer = GRPOTrainer(\n"
    "    model=model, tokenizer=tokenizer,\n"
    "    train_dataset=full_dataset, args=full_cfg,\n"
    "    **_reward_kwargs,\n"
    ")\n"
    "print('Phase 3: Full GRPO starting...')\n"
    "full_trainer.train()\n"
    "print('Phase 3 complete!')"
))

# ── Cell 10: Extract metrics ──
cells.append(cell(
    "# Cell 10: Extract metrics (handles all TRL key variants)\n"
    "log = full_trainer.state.log_history\n"
    "print('All logged keys:', set(k for x in log for k in x))\n\n"
    "def extract(entries, keys):\n"
    "    for k in keys:\n"
    "        s = [x['step'] for x in entries if k in x]\n"
    "        v = [x[k] for x in entries if k in x]\n"
    "        if s:\n"
    "            print(f'  key={k!r} ({len(s)} pts)')\n"
    "            return s, v\n"
    "    print(f'  Not found among: {keys}')\n"
    "    return [], []\n\n"
    "reward_steps, reward_vals = extract(log,\n"
    "    ['reward', 'rewards/mean', 'reward_mean', 'train/reward', 'rewards'])\n"
    "loss_steps, loss_vals = extract(log,\n"
    "    ['loss', 'train/loss', 'train_loss'])\n"
    "print(f'Rewards: {len(reward_steps)} pts | Loss: {len(loss_steps)} pts')"
))

# ── Cell 11: Reward curve ──
cells.append(cell(
    "# Cell 11: reward_curve.png\n"
    "import matplotlib.pyplot as plt, numpy as np\n\n"
    "fig, ax = plt.subplots(figsize=(10, 6))\n"
    "if reward_steps:\n"
    "    ax.plot(reward_steps, reward_vals, '#2563eb', lw=2, label='GRPO reward')\n"
    "    if len(reward_steps) > 3:\n"
    "        z = np.polyfit(reward_steps, reward_vals, 1)\n"
    "        ax.plot(reward_steps, np.poly1d(z)(reward_steps),\n"
    "                '--', color='#93c5fd', alpha=0.7, label='trend')\n"
    "    ax.legend()\n"
    "    ax.set_ylabel('Mean Reward')\n"
    "else:\n"
    "    # Fallback to SFT loss\n"
    "    ss = [x.get('step', i) for i, x in enumerate(sft_log) if 'loss' in x]\n"
    "    sv = [x['loss'] for x in sft_log if 'loss' in x]\n"
    "    ax.plot(ss, sv, '#2563eb', lw=2)\n"
    "    ax.set_ylabel('SFT Loss (GRPO rewards not logged)')\n\n"
    "ax.set_xlabel('Training Step')\n"
    "ax.set_title('M&A RL - Reward Curve (GRPO, Qwen2.5-3B)')\n"
    "ax.grid(True, alpha=0.3)\n"
    "fig.savefig('reward_curve.png', dpi=150, bbox_inches='tight')\n"
    "plt.show(); print('Saved reward_curve.png')"
))

# ── Cell 12: Loss curve ──
cells.append(cell(
    "# Cell 12: loss_curve.png (SFT + GRPO combined)\n"
    "import matplotlib.pyplot as plt\n\n"
    "fig2, ax2 = plt.subplots(figsize=(10, 6))\n"
    "ss = [x.get('step', i) for i, x in enumerate(sft_log) if 'loss' in x]\n"
    "sv = [x['loss'] for x in sft_log if 'loss' in x]\n"
    "if ss:\n"
    "    ax2.plot(ss, sv, '#f59e0b', lw=2, label='Phase 1: SFT')\n"
    "if loss_steps:\n"
    "    offset = (max(ss) + 1) if ss else 0\n"
    "    ax2.plot([s + offset for s in loss_steps], loss_vals,\n"
    "             '#dc2626', lw=2, label='Phase 3: GRPO')\n"
    "if not ss and not loss_steps:\n"
    "    ax2.text(0.5, 0.5, 'No loss data', transform=ax2.transAxes, ha='center')\n\n"
    "ax2.set_xlabel('Training Step')\n"
    "ax2.set_ylabel('Loss')\n"
    "ax2.set_title('M&A RL - Loss Curve (SFT + GRPO, Qwen2.5-3B)')\n"
    "ax2.grid(True, alpha=0.3)\n"
    "if ss or loss_steps: ax2.legend()\n"
    "fig2.savefig('loss_curve.png', dpi=150, bbox_inches='tight')\n"
    "plt.show(); print('Saved loss_curve.png')"
))

# ── Cell 13: Sample outputs ──
cells.append(cell(
    "# Cell 13: Post-training output samples (hacking check)\n"
    "FastLanguageModel.for_inference(model)\n"
    "print('=== Post-Training Samples ===')\n"
    "for i in range(5):\n"
    "    obs = env.reset(seed=100+i)\n"
    "    inputs = tokenizer(format_prompt(obs.task_prompt, obs.deal_excerpt),\n"
    "                       return_tensors='pt').to(model.device)\n"
    "    with torch.no_grad():\n"
    "        out = model.generate(**inputs, max_new_tokens=256,\n"
    "                             do_sample=True, temperature=0.7)\n"
    "    text = tokenizer.decode(out[0][inputs['input_ids'].shape[1]:],\n"
    "                            skip_special_tokens=True).strip()\n"
    "    obs2 = env.step(Action(agent_output=text, action_type='identify'))\n"
    "    print(f'[{i+1}] reward={obs2.reward:.3f} | {text[:180]}')"
))

# ── Cell 14: Save model ──
cells.append(cell(
    "# Cell 14: Save — MUST use save_pretrained_merged (not save_pretrained)\n"
    "FastLanguageModel.for_training(model)\n"
    "model.save_pretrained_merged('final_model', tokenizer, save_method='merged_16bit')\n"
    "print('Saved: final_model/')"
))

# ── Cell 15: Commit ──
cells.append(cell(
    "# Cell 15: Commit training curves to repo\n"
    "!git add reward_curve.png loss_curve.png\n"
    "!git commit -m 'Add training curves (SFT+GRPO, Qwen2.5-3B, T4)'\n"
    "!git push"
))

# ── Cell 16: Cleanup ──
cells.append(cell(
    "# Cell 16: Cleanup\n"
    "server_proc.terminate()\n"
    "print('Done! Artifacts: reward_curve.png  loss_curve.png  final_model/')"
))

# ── Write notebook ──
nb = {
    "nbformat": 4, "nbformat_minor": 0,
    "metadata": {
        "colab": {"provenance": [], "gpuType": "T4"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU",
    },
    "cells": cells,
}

out = os.path.join(os.path.dirname(__file__), "grpo_training.ipynb")
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)
print(f"Written: {out}  ({os.path.getsize(out):,} bytes)")
