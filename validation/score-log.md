# Test-set score log

Every evaluation on a held-out **test** set is recorded here, append-only. The headline score on a test set is its first look, in total, not per model version. Later looks are logged with a running look number and labelled "test reused (look n)" (validation/forecast-protocol.md §6).

| Date (UTC) | Model | Version | Test set | Protocol commit | Look # | Bundle sha256 | Truth sha256 (Kp, Dst) | Input manifest sha256 | Metrics file | Commit |
|---|---|---|---|---|---|---|---|---|---|---|

## Replays (not scores; validation/forecast-protocol.md §7)

| Date (UTC) | Event | Bundle sha256 | Protocol commit | Outputs file | Commit |
|---|---|---|---|---|---|
