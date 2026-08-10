# 16. Interview Prep

> **Category:** Certification & Interview Preparation

The CNCF offers three hands-on Kubernetes certifications, plus a large set of **conceptual interview questions**. This section maps the official exam curricula to the docs above, lists the exact `kubectl` commands the exams reward, and gives you the most common interview Q&A.

## Structure

| File | Topic |
|------|-------|
| [cka.md](cka.md) | CKA (admin) — cluster ops, troubleshooting, networking, storage |
| [ckad.md](ckad.md) | CKAD (app dev) — designing/configuring apps, probes, services |
| [cks.md](cks.md) | CKS (security) — hardening, NetworkPolicies, secrets, admission |
| [interview-questions.md](interview-questions.md) | Conceptual interview questions + answers |
| [advanced-questions.md](advanced-questions.md) | System-design / whiteboard-style K8s questions |

## Certification Matrix

| Exam | Focus | Prereqs | Passing | Hands-on? |
|------|-------|---------|---------|-----------|
| **CKA** | Cluster admin (install, configure, troubleshoot, upgrade) | — | 66% (42/65 min) | ✅ Yes (live cluster) |
| **CKAD** | App dev/delivery (design, config, rollout) | — | 66% (38/75 min) | ✅ Yes (live cluster) |
| **CKS** | Cluster + app security hardening | **CKA required** first | 66% (75 min) | ✅ Yes (live cluster) |

### Domain weighting (current as of v1.30-1.31)

| Domain | CKA | CKAD | CKS |
|--------|-----|------|-----|
| Cluster Architecture, Installation & Configuration | 25% | — | — |
| Workloads & Scheduling | 15% | — | 11% |
| Services & Networking | 20% | — | — |
| Storage | 10% | — | — |
| Troubleshooting | 30% | — | 15% |
| — | — | Core Concepts (16%) | — |
| — | — | Configuration (17%) | — |
| — | — | Multi-container pods (10%) | — |
| — | — | Observability (15%) | — |
| — | — | Services & Networking (21%) | — |
| — | — | — | Cluster Hardening (21%) |
| — | — | — | Cluster Hardening (18%) |
| — | — | — | Network Security (7%) |
| — | — | — | Sec. & Supply Chain (11%) |

> **Note:** these percentages shift slightly between versions; check the [certification page](https://www.cncf.io/certification/). What does NOT change is the exam format: **2-hour, proctored, live-cluster** — you get a terminal and a browser tab of docs. The only site allowed is `kubernetes.io/docs` + `kubernetes.io/blog`.

## Exam Strategy

| Tip | Why |
|-----|-----|
| `kubectl explain` is your friend | You don't have to *memorize* every field — look it up. Memorize the *shape* of Pods/Deployments. |
| Use `--dry-run=client -o yaml > file.yaml` | Write YAML safely without touching the cluster until you're sure. |
| Alias `k=kubectl`, `export do=--dry-run=client -o yaml` | You type ~50 commands; aliases save minutes. |
| Tab-completion | Enable it (`source <(kubectl completion bash)`). |
| Time budget | ~5 min per question; mark hard ones, come back. |
| Save often | The terminal state isn't lost between questions, but be tidy. |

## Quick Command Cheatsheet (exam-takers read this first)

```bash
k run nginx --image=nginx --restart=Never --port=80 --rm -i --tty -- sh
k expose pod nginx --port=80 --target-port=8080
k create deploy web --image=nginx --port=80
k create deploy web --image=nginx --port=80 --replicas=3 --dry-run=client -o yaml > w.yaml
k get deploy,svc,rs,po -o wide
k describe secret my-secret -o jsonpath='{.data.token}' | base64 -d
k apply -f https://k8s.io/examples/...                  # allowed from browser
k auth can-i '*'                                       # quick RBAC smoke test
```

## Related Resources

- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
- [Security](../06-security/README.md)
- [Networking](../04-networking/README.md)
- [Storage](../05-storage/README.md)
- [Troubleshooting](../14-troubleshooting/README.md)
