# CI/CD Examples

> GitOps-ready manifests for Argo CD and Flux.

## Contents
- `argocd-app.yaml` — a minimal Argo CD Application (Git -> cluster).
- `flux-kustomization.yaml` — a Flux Kustomization pulling a Git repo.

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
