# Scheduling Examples

> Manifests for HPAs, VPA, resource quotas, limit ranges, PDBs, taints/tolerations, and affinity.

## Contents
- `hpa.yaml` — HorizontalPodAutoscaler (v2) — CPU + external metric with scale-down/up stabilization.
- `pod-disruption-budget.yaml` — PodDisruptionBudget (policy/v1) — minAvailable + namespace-wide PDB.
- `resource-quota-limitrange.yaml` — Namespace + ResourceQuota + LimitRange (with a FinOps cost-team label).
- `taints-tolerations-affinity.yaml` — tolerations + nodeSelector + podAntiAffinity + nodeAffinity.

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
