# CKAD — Certified Kubernetes Application Developer

> **Category:** Certification

## Exam At-a-Glance

| Item | Value |
|------|-------|
| Provider | CNCF |
| Duration | 75 minutes |
| Questions | ~12–14 performance-based tasks |
| Passing score | 66% |
| Required prerequisite | None |
| Allowed docs | `kubernetes.io/docs`, `kubernetes.io/blog`, `github.com/kubernetes/*` |
| Result time | ~72 hours |

## Domain Breakdown

| Domain | Weight | What it covers |
|--------|--------|----------------|
| **Core Concepts** | 16% | Pods, Services, Deployments, labels/selectors |
| **Configuration** | 17% | ConfigMaps, Secrets, Env vars, `kubectl create` with `--from-envFile` |
| **Multi-container Pods** | 10% | Sidecars, init containers, shared volumes, `shareProcessNamespace` |
| **Observability** | 15% | Liveness/readiness probes, Container/Pod resource metrics |
| **Services & Networking** | 21% | Services (ClusterIP/NodePort/LoadBalancer), DNS, NetworkPolicies |
| **Kubernetes Cluster / Troubleshooting** | 26% | rolling updates, `kubectl rollout`, `kubectl apply/patch`, debugging |

> **26% troubleshooting** + **21% networking** — these two alone are ~half the exam. They map heavily to the docs in [Networking](../04-networking/README.md) and [Troubleshooting](../14-troubleshooting/README.md).

## Must-Know Commands

```bash
# --- Fast manifest authoring ---
k create cm my-config --from-literal=LOG_LEVEL=debug
k create cm my-config --from-env-file=env.txt
k create secret generic my-secret --from-literal=PASS=p4ss --from-file=key.pem
k create secret generic my-secret --from-literal=PASS=p4ss \
  --dry-run=client -o yaml | k apply -f -                 # idempotent

# --- Env + volume from config/secret ---
envFrom:
- configMapRef:
    name: my-config
env:
- name: API_KEY
  valueFrom:
    secretKeyRef:
      name: my-secret
      key: api-key

# --- Probes ---
readinessProbe:
  httpGet: { path: /healthz, port: 8080 }   # for Service endpoints
  initialDelaySeconds: 5
livenessProbe:                              # for restart decisions
  exec: { command: ["cat", "/tmp/healthy"] }
  periodSeconds: 5

# --- Multi-container Pod (sidecar pattern) ---
spec:
  containers:
  - name: app
  - name: nginx-proxy  # sidecar
    image: nginx
    volumeMounts: [{name: shared, mountPath: /usr/share/nginx/html}]
  volumes:
  - name: shared
    emptyDir: {}

# --- Rolling update control ---
k set image deployment/web app=nginx:v2
k rollout status deployment/web
k rollout pause deployment/web      # canary / manual gate
k rollout undo deployment/web
k rollout history deployment/web
```

## High-Yield Tasks

| Task | Where to study |
|------|----------------|
| Mount a config dir from a ConfigMap | [configmaps.md](../01-core-concepts/configmaps.md) |
| Share an `emptyDir` between app + sidecar | [volumes.md](../01-core-concepts/volumes.md) |
| Set CPU/memory requests + limits | [resources.md](../07-scheduling-autoscaling/resources.md) |
| Tune a readiness probe so a Pod enters the Service endpoints | [services.md](../04-networking/services.md) |
| Update a Deployment and roll back on failure | [deployments.md](../03-workloads/deployments.md), [deployment-strategies.md](../03-workloads/deployment-strategies.md) |
| Expose a Pod with a NodePort / LoadBalancer | [services.md](../04-networking/services.md) |
| Restrict traffic with a NetworkPolicy | [network-policies.md](../04-networking/network-policies.md) |

## Multi-container Pod Patterns (the 10% that trips people up)

The Pod spec is one `spec.template.spec` with **multiple** `containers:` entries. Key gotchas:

- **`emptyDir` is the shared volume** (lives as long as the Pod). `hostPath` works but is node-pinned.
- A **sidecar** shares the Pod's network namespace → it connects to the main container over `localhost`.
- **Init containers** run to completion *before* the main ones, serially, and have their own image/lifecycle.
- `shareProcessNamespace: true` lets a sidecar `ls /proc/1/root` (the app) — powerful for debugging side-by-side.

```yaml
apiVersion: v1
kind: Pod
spec:
  shareProcessNamespace: true
  initContainers:
  - name: wait-for-db
    image: busybox
    command: ["sh", "-c", "until nc -z db:5432; do sleep 1; done"]
  containers:
  - name: app
    image: myapp
  - name: sidecar
    image: busybox
    command: ["sh", "-c", "tail -f /proc/1/fd/1"]
```

## Observability: Probes & Resources

### Probe types
| Probe | How | Use |
|-------|-----|-----|
| `httpGet` | `GET path:port` → 200 = healthy | HTTP apps, liveness on `/healthz` |
| `tcpSocket` | TCP connect succeeds | DB, message brokers |
| `exec` | command returns 0 | custom scripts |
| `grpc` | gRPC health-check port | gRPC servers (1.27+) |

### Resource requests/limits + QoS
```yaml
resources:
  requests: { cpu: "100m", memory: "128Mi" }
  limits:   { cpu: "250m", memory: "256Mi" }
```
- Set `requests` for scheduling; `limits` to cap. A Pod with `requests == limits` is **Guaranteed** QoS (highest eviction priority).

## Troubleshooting Workflow

1. `kubectl get pod,svc -o wide` — names + Node IPs.
2. `kubectl describe pod <p>` — Events show `FailedMount`, `FailedScheduling`, probe failures.
3. `kubectl logs <p>` + `kubectl logs -p <p>` — current vs. previous.
4. `kubectl get endpoints <svc>` — empty? selector mismatch or Pods not Ready.
5. `kubectl get networkpolicy -n <ns>` — silent deny-all once a policy exists.
6. For a **stuck rollout**: `kubectl rollout status`, then `kubectl describe deploy`, check the new ReplicaSet's Pod `phase`/`containerStatuses`.

## Common CLI Shorteners (exam speed)

```bash
alias k=kubectl
export now="--force --grace-period=0"
export do="--dry-run=client -o yaml"
# Create from URL, write to file, apply:
kubectl create deploy web --image=nginx --dry-run=client -o yaml > w.yaml
# Patch without editing YAML:
kubectl set resources deploy/web -c web --requests=cpu=100m,memory=128Mi
kubectl patch deployment web -p '{"spec":{"replicas":3}}'
```

## Interview Questions (CKAD-flavored)

**Q: When should a Service have a readiness probe vs a liveness probe?**
A: Readiness controls whether a Pod joins the Service endpoints (traffic). Liveness controls restarts. Put readiness on the *app's health endpoint*; put liveness on something that reliably crashes if the app hangs (an exec health check or a port that only opens when ready). If both use `/healthz` and it flaps, you get restart storms — separate them (e.g., `liveness: /livez`, `readiness: /readyz`).

**Q: How do you make a Deployment update roll out slowly?**
A: Set `spec.strategy.rollingUpdate.maxSurge` and `maxUnavailable` (e.g., `maxSurge: "25%"`, `maxUnavailable: "0%"` rolls all at once but keeps availability). Pause mid-rollout (`kubectl rollout pause`), edit, then `kubectl rollout resume`. The `revisionHistoryLimit` controls how many old ReplicaSets to keep for `kubectl rollout undo`.

**Q: What is the difference between a ConfigMap and a Secret?**
A: A Secret is **base64-encoded** (not encrypted) data typed as `Opaque` (or `kubernetes.io/dockerconfigjson` for image pulls); a ConfigMap is plain string data. Both mount identically (volume or `envFrom`/`valueFrom`). Secrets aren't safe at rest unless etcd is encrypted (`EncryptionConfiguration`).

**Q: How does a sidecar container communicate with the main container?**
A: They share the **same network namespace** → the sidecar talks to the main container over `localhost:<port>`. For files, an `emptyDir` volume mounted into both lets the sidecar read what the main wrote.

## Related Resources

- [CKA](cka.md)
- [CKS](cks.md)
- [Services](../04-networking/services.md)
- [Network Policies](../04-networking/network-policies.md)
- [Deployments](../03-workloads/deployments.md)
- [ConfigMaps & Secrets](../01-core-concepts/configmaps.md)
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
