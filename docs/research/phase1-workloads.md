# Phase 1 research: reference AI workloads, fault injection, fleet SDC

Source: `researcher` subagent (Sonnet), 2026-10-06. Many web pages were read through a summarising fetch tool (marked PROXY in the researcher's output). Every value used in `validation/reference/workloads.yaml` was re-checked directly by the main agent (HF API, model config, Qwen blog, torchvision docs, GitHub API) and is marked **[verified]**.

## Reference models
- **ResNet-50**
  - He et al. 2016 (`he2016resnet`): "3.8 billion FLOPs", with FLOPs defined as multiply-adds (Table 1, §4.1), for 224×224 ImageNet inputs. The paper does not give the ImageNet parameter count.
  - torchvision `ResNet50_Weights.IMAGENET1K_V1` (`torchvision_resnet50_weights`) **[verified]**: num_params 25,557,032; acc@1 76.13; acc@5 92.862; "GFLOPS 4.09"; file size 97.8 MB.
  - torchvision ResNet is "V1.5" (stride on the 3×3 conv), so 3.8 vs 4.09 differ by model variant and counting tool. Never mix the two without saying which.
  - torchvision code licence: BSD-3-Clause (`torchvision_repo`) **[verified]**. Terms for the ImageNet-trained weights are not researched (UNVERIFIED).
- **Qwen2.5-1.5B** (recommended LLM; `hf_qwen25_15b`, `qwen2025blog`) **[verified]**:
  - 1,543,714,304 parameters (1.31B non-embedding)
  - Apache-2.0, not gated
  - bfloat16 weights, 28 layers, hidden size 1536
  - context 32K per the blog table; config `max_position_embeddings` is 131072
  - base-model MMLU 60.9
- **Alternatives** (PROXY, not used in the reference set):
  - Llama 3.2 1B: 1,235,814,400 params; Llama 3.2 Community License with naming, attribution and acceptable-use clauses; gated. Fault-injected by `chai2025llmgpu`, so useful for comparison.
  - OLMo-2-0425-1B: 1,484,916,736 params; Apache-2.0; 4K context.
  - Gemma 3 1B: 999,885,952 params; gated; its terms were not read.
  - Qwen3-1.7B-Base: 1,720,574,976 params; Apache-2.0.

## Fault-injection studies (Phase 4 references)
- **Li et al. SC'17 (`li2017sc`)**: simulated DNN accelerator, single transient bit flips.
  - The SDC probability (top-1 changes, per activated fault) depends strongly on data type: AlexNet 7.19% (32b_rb10) vs 0.38% (FLOAT).
  - Flipping bit 30 gives 26.65% vs 0.22% across formats.
  - Only high-order exponent bits matter for floating point, and 0→1 flips matter most.
  - Raw rate 20.49 FIT/Mb is an extrapolation, not a measurement.
  - Detector: §6.2 averages are precision 90.21% and recall 92.5%. The abstract quotes different "selected" values; the paper is internally inconsistent here.
- **PyTorchFI (`mahmoud2020pytorchfi`)**: one INT8 neuron flip in each of more than 1e7 injections across 6 ImageNet networks. "A little less than 1%" caused a top-1 change. Per-network values are bar heights only, so don't use them as registry values.
- **Chai et al. 2025 (`chai2025llmgpu`)**: NVBitFI on an A100, flipping GPU register bits during LLM inference.
  - The single-fault abnormal rate (SDC + DUE) is 0.17–0.29 across 6 models (Llama3.2-1B 0.212, Qwen3-1.7B 0.238). Most of it is DUE (crashes, illegal memory accesses).
  - It rises to more than 75% at 8 faults.
  - Bit-30 SDC is ~24%; low-order bits are below 1%.
  - "3,000 injections … exactly 200 SDC" is ambiguous (per model or in total).
  - Not peer reviewed.
- **Leads only** (PROXY or blocked, UNVERIFIED): Hong et al. 2019 (`hong2019tbd`), Das et al. 2024 (`das2024attentionbreaker`), Guo et al. 2025 (`guo2025sbfa`), Reagen et al. 2018 Ares (`reagen2018ares`, publisher 403).
  - These are mostly *targeted attacks*. They are worst-case bounds, not soft-error rates.

## Fleet SDC and hardware-failure rates
- **Google (`hochschild2021cores`)**: "a few mercurial cores per several thousand machines". No exact rate is published, and the cause is defects, not radiation.
- **Meta (`dixit2021sdc`)**: "hundreds of CPUs" detected across "hundreds of thousands of machines". No usable point estimate. SDCs are "not limited to soft errors due to radiation".
- **Llama 3 (`grattafiori2024llama3` §3.3.4, Table 5; PROXY)**: in 54 days on up to 16K H100s there were 419 unexpected interruptions, including:
  - GPU HBM3 memory: 72
  - GPU SRAM: 19
  - silent data corruption: 6
  - The "Faulty GPU 148 = 30.1%" row is inconsistent (148/419 = 35.3%), so check the PDF before citing it.
  - Per-GPU-hour rates derived from this assume all 16,384 GPUs ran for 54 days, so they are UNVERIFIED. They are ground-fleet hardware failures, not radiation SEU rates.
- **Ma et al. 2025 (`ma2025sdctraining`)**: SDCs can shift training to different optima and cause loss spikes. Qualitative only.
