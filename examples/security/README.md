# Security Examples

> RBAC, NetworkPolicy, PSA namespace labels, and egress restriction patterns.

## Contents
- `network-policy-egress.yaml` — default-deny ingress/egress + allow egress to a Redis service + DNS, plus a default-deny-all catch-all.
- `pod-security-baseline.yaml` — Namespace labeled for Pod Security Admission `baseline`/`restricted` tiers.
- `rbac-rolebinding.yaml` — least-privilege Role + RoleBinding for a service account.
- `restrict-egress.yaml` — deny all egress, allow one namespace/service.

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
