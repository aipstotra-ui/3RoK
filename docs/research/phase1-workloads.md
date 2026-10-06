# Phase 1 research: reference AI workloads, fault injection, fleet SDC

Source: `researcher` subagent (Sonnet), 2026-10-06, plus direct checks by the main agent.

How each item was read:
- **[verified]**: re-checked directly by the main agent (HF API and config, licence text, Qwen blog, torchvision docs, GitHub API).
- **[direct]**: read as full text by the researcher, not re-checked.
- **[PROXY]**: read only through a summarising fetch tool; treat as a lead and re-read before use.

Every value in `validation/reference/workloads.yaml` is **[verified]**.

## Reference models (in workloads.yaml)
- **ResNet-50**
  - torchvision `ResNet50_Weights.IMAGENET1K_V1` (`torchvision_resnet50_weights`) **[verified]**:
    - num_params 25,557,032
    - acc@1 76.13, acc@5 92.862
    - "GFLOPS 4.09" (the counting convention is not stated on the page)
    - file 97.8 MB
  - torchvision ResNet is "V1.5" (stride on the 3×3 conv). The original paper (`he2016resnet`) **[direct]** gives "3.8 billion FLOPs" for its V1 model, with FLOPs defined as multiply-adds. Never mix the two figures.
  - Code licence BSD-3-Clause (`torchvision_repo`) **[verified]**. Terms for the ImageNet-trained weights: UNVERIFIED.
- **NVIDIA Nemotron-3-Nano-4B** (reference LLM, chosen by Aiden 2026-10-06; `hf_nemotron3_nano_4b`) **[verified]**:
  - 3,973,556,832 parameters; bfloat16; not gated; released 2026-03-07
  - base_model `nvidia/NVIDIA-Nemotron-Nano-9B-v2`
  - config: `NemotronHForCausalLM`, 42 layers, hidden size 3136, `max_position_embeddings` 262144
  - `hybrid_override_pattern` `M-M-M-MM-M-M*-M-M*-M-M-M*-M-M-MM*-MMM-M-M-`, i.e. mostly Mamba-2 blocks with a few attention blocks: a hybrid Mamba-Transformer
- **NVIDIA Nemotron Open Model License** (`nvidia_nemotron_oml`) **[verified]**, read directly:
  - "Works are commercially usable. You are free to create and distribute Derivative Works. NVIDIA does not claim ownership to any outputs."
  - §3 Redistribution: give recipients a copy of the licence, keep the attribution notices, and include the notice "Licensed by NVIDIA Corporation under the NVIDIA Nemotron Model License."
- **Why Nemotron:** Aiden prefers NVIDIA-built models (audience fit, origin). It is a hybrid architecture, and the published bit-flip studies below cover Transformers only. So Phase 4 results for it would be new, and also have no external comparison point.

## Alternatives considered (not in workloads.yaml)
- **Qwen2.5-1.5B** (`hf_qwen25_15b`, `qwen2025blog`) **[verified]**: 1,543,714,304 params, Apache-2.0, ungated, bf16, MMLU 60.9 (base). It was the first pick on licence grounds and was replaced by Aiden's NVIDIA preference.
- **Nemotron-Flash-1B** **[verified]**: 965,389,440 params, but licensed **CC-BY-NC-4.0** (non-commercial), so unsuitable.
- **[PROXY] leads:**
  - Llama 3.2 1B (`hf_llama32_1b`): 1,235,814,400 params; Llama 3.2 Community License; gated. It is fault-injected by `chai2025llmgpu`, which makes it the natural *comparison* model if one is ever needed.
  - OLMo-2-0425-1B (`hf_olmo2_1b`): Apache-2.0, fully open data.
  - Gemma 3 1B (`hf_gemma3_1b`): gated; terms not read.
  - Qwen3-1.7B-Base (`hf_qwen3_17b_base`).

## Fault-injection studies (Phase 4 references)
**Cross-study rates are not comparable** unless the fault model (datapath, register or memory), the injection site, whether the fault was activated, and the number format all match. Note that bf16 has fp32's 8 exponent bits, so FLOAT16 results do not transfer to bf16.

- **Li et al. SC'17 (`li2017sc`) [direct]:**
  - Setup: simulated DNN-accelerator datapath and buffers; single transient bit flips; 3,000 faults per latch.
  - Denominator: per **activated** fault. Outcome: SDC-1 (top-1 changes).
  - AlexNet: 7.19% (32b_rb10) vs 0.38% (FLOAT).
  - Bit 30 in CaffeNet: 26.65% (32b_rb10) vs 0.22% (32b_rb26).
  - Only high-order exponent bits matter for floating point; 0→1 flips matter most.
  - "Raw rate 20.49 FIT/Mb" is the paper's projection for 16 nm, scaled from a 28 nm neutron soft-error figure it cites (Neale et al.). It is a ground-level, extrapolated number: **not an orbital rate; do not use it as an SEU input.**
  - Detector §6.2 averages: precision 90.21%, recall 92.5%. The abstract quotes different "selected" values, an internal inconsistency in the paper.
- **PyTorchFI (`mahmoud2020pytorchfi`) [direct]:**
  - Setup: one INT8 neuron (activation) flip per inference, more than 1e7 injections across 6 ImageNet networks.
  - Denominator: per **injection**. Outcome: top-1 misclassification.
  - "A little less than 1%" overall. Per-network values are bar heights only (do not use them as registry values).
- **Chai et al. 2025 (`chai2025llmgpu`) [direct]:**
  - Setup: NVBitFI on an A100, flipping **GPU destination-register** bits during LLM inference; not peer reviewed.
  - Denominator: per **injection run**. Outcome: SDC + DUE combined (most is DUE: crashes, illegal memory accesses).
  - Single-fault abnormal rate 17–29% across 6 models (Llama3.2-1B 21.2%, Qwen3-1.7B 23.8%), rising to more than 75% at 8 faults per run.
  - Per-bit tests (500 injections each): bit-30 SDC about 24%; low-order bits below 1%.
  - "3,000 injections … exactly 200 SDC" is ambiguous (per model or in total).
  - The arXiv ID (2601.xxxxx) vs the "v1 dated 25 Dec 2025" consistency is not verified.
- **Leads only** ([PROXY] or blocked; UNVERIFIED):
  - Hong et al. 2019 (`hong2019tbd`)
  - Das et al. 2024 (`das2024attentionbreaker`)
  - Guo et al. 2025 (`guo2025sbfa`)
  - Reagen et al. 2018 Ares (`reagen2018ares`, publisher 403)

  The first three are mostly *targeted attacks*: worst-case bounds, not soft-error rates.

## Fleet SDC and hardware-failure reports (ground fleets, not radiation)
- **Google (`hochschild2021cores`) [direct]:** "a few mercurial cores per several thousand machines". No exact rate is published, and the cause is defects, not radiation.
- **Meta (`dixit2021sdc`) [direct]:** "hundreds of CPUs" detected across "hundreds of thousands of machines". No usable point estimate. SDCs are "not limited to soft errors due to radiation".
- **Llama 3 (`grattafiori2024llama3` §3.3.4, Table 5) [PROXY]:**
  - In a 54-day snapshot on **up to** 16K H100s there were 419 unexpected **job interruptions** (events that stopped the job, not per-device failures). They include:
    - GPU HBM3 memory: 72
    - GPU SRAM: 19
    - silent data corruption: 6
  - The SDC count covers only corruptions that were **detected** and stopped the job, so it is a lower bound.
  - The "Faulty GPU 148 = 30.1%" row is inconsistent (148/419 = 35.3%); check the PDF before citing it.
  - Any per-GPU-hour rate needs an assumed GPU count and duration (UNVERIFIED), and it is not a radiation SEU rate.
- **Ma et al. 2025 (`ma2025sdctraining`) [PROXY, abstract]:** SDCs can shift training to different optima and cause loss spikes. Qualitative only.
