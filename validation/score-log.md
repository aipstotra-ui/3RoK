# Test-set score log

Every evaluation on a held-out **test** set is recorded here, append-only. The headline score on a test set is its first look, in total, not per model version. Later looks are logged with a running look number and labelled "test reused (look n)" (validation/forecast-protocol.md §6).

| Date (UTC) | Model | Version | Test set | Protocol commit | Look # | Artifact sha256 | Metrics file | Commit |
|---|---|---|---|---|---|---|---|---|
