# Lab: Build a Secure, Observable App (end-to-end)

> Walk through the full lifecycle: deploy a Pod, expose it, add autoscaling, lock it down with a NetworkPolicy, attach a secret, and mount storage. Mirrors the [CKA/CKAD/CKS walkthrough](../../16-interview-prep/exam-walkthrough.md).

## Setup
```bash
export k=kubectl
# 1. Create a fresh namespace
k create ns lab
k config set-context --current --namespace=lab
```

## Step 1 — Run the app
```bash
# Use a real image that listens on 80
k create deployment web --image=nginx:1.25 --port=80
k scale deploy web --replicas=3
k get pods -o wide
```

## Step 2 — Expose it inside the cluster, then outside
```bash
k expose deploy web --port=80 --target-port=80 --name web-svc
k get svc,ep web-svc                 # confirm endpoints are non-empty
# Outside (local kind/minikube clusters):
k expose deploy web --type=NodePort --port=80 --name web-node --dry-run=client -o yaml | k apply -f -
```

## Step 3 — Add TLS + Ingress
```bash
k create secret tls web-tls --cert=tls.crt --key=tls.key   # self-signed for the lab
# apply examples/common-patterns/ingress.yaml (update host + secret name)
k apply -f ../networking/../../examples/common-patterns/ingress.yaml
```

## Step 4 — Autoscale it
```bash
k apply -f examples/scheduling/hpa.yaml           # CPU>60% scales out
# watch:
k get hpa -w
```

## Step 5 — Lock down (NetworkPolicy)
```bash
# default deny all, then allow:
k apply -f examples/security/network-policy-egress.yaml
k get netpol
```

## Step 6 — Attach config + secret
```bash
k apply -f examples/common-patterns/configmap-secret.yaml
k exec -it deploy/web -- env | grep -E 'LOG_LEVEL|USERNAME'
```

## Step 7 — Attach storage
```bash
k apply -f examples/storage/pvc-deployment.yaml
k get pvc
```

## Step 8 — Inspect & debug
```bash
k describe pod <pod>              # read Events
k logs -f deploy/web              # or k logs -p <pod>
k get events -n lab --sort-by=.lastTimestamp
k top pods                         # needs metrics-server
k port-forward svc/web-svc 8080:80
curl -s localhost:8080 | head
```

## Teardown
```bash
k delete ns lab
```

## Expected outcomes
- `web-svc` resolves inside the cluster (`nslookup web-svc`).
- `k get endpoints web-svc` shows **3** addresses (one per pod).
- Scaling traffic up drives the HPA from 3 → more pods.
- NetPol blocks egress to `redis` and the internet, but allows DNS + same-namespace.

## Related
- [Troubleshooting Encyclopedia](../../14-troubleshooting/troubleshooting-encyclopedia.md) · [Exam walkthrough](../../16-interview-prep/exam-walkthrough.md) · [FinOps](../../08-cluster-operations/finops.md)
EOFMARKER
echo "lab: lab-instructions.md written ($(wc -l < common-patterns/lab-instructions.md) lines)"