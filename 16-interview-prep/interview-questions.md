# Kubernetes Interview Questions

> **Category:** Interview Preparation

These are the conceptual questions most often asked of Kubernetes engineers, SREs, and platform teams. Each maps to a doc in this repo so you can drill into the "why".

## Core Concepts

**Q1: What is the difference between a Pod, a Deployment, and a ReplicaSet?**
A: A **Pod** is the smallest unit (one or more containers sharing a network namespace). A **ReplicaSet** is a controller whose *only* job is to keep N copies of a Pod-template alive (it creates/terminates Pods). A **Deployment** is a higher-level controller that manages a ReplicaSet — it provides the *rollout* semantics (rolling updates, pause, rollback) on top of the ReplicaSet's "maintain N replicas". Most workloads use a Deployment, which owns a ReplicaSet, which owns Pods.

**Q2: What does a Pod's `spec.restartPolicy` actually do?**
A: `restartPolicy` controls what the **kubelet** does if a container in the Pod exits. `Always` (default for Deployments) restarts on any exit. `OnFailure` restarts only when the exit code is non-zero (typical for Jobs). `Never` means never restart (one-shot). It does NOT cross Node boundaries — if the Node dies, the kubelet's state is lost and the Deployment/ReplicaSet schedules a new Pod elsewhere.

**Q3: What is the difference between a Service and an Ingress?**
A: A **Service** is a logical network endpoint (ClusterIP + selector → Pod IPs), giving Pods a stable address and basic load balancing inside the cluster. An **Ingress** is an L7 routing rule that sits *on top* of Services — it routes HTTP(S) by host/path to (usually) Services. You need an **Ingress Controller** (NGINX, Traefik) to actually implement it. Think: Service = TCP load balancer; Ingress = HTTP virtual-host router.

## Scheduling & Controllers

**Q4: When does the scheduler make a decision, and what can block it?**
A: The scheduler only acts on **unscheduled** Pods (`spec.nodeName` empty). It filters Nodes by feasibility (resource, nodeSelector, taints/tolerations, affinity) then scores them. It's blocked if no Node satisfies the constraints — that shows up as `Pending` + a `FailedScheduling` event. **Note:** `kube-scheduler` only *places* pods; `kube-controller-manager` (replicaset/node/controller etc.) *reacts* to changes.

**Q5: Explain the difference between `requests` and `limits`.**
A: `requests` = the *guaranteed* CPU/Mem the scheduler uses to place a Pod (Node must have that much free). `limits` = a hard *ceiling*. For CPU, a container can use the node's CPU if the core is idle even past its limit, but **is throttled** if it hits `cpu.cfs_quota_us`. For memory, hitting the limit triggers an **OOMKill** (exit 137) — no throttling, just killed. Setting `limit >= request` is required; `request == limit` yields QoS `Guaranteed`.

**Q6: What happens to a Pod whose Node is cordoned + drained?**
A: Cordon (`SchedulingDisabled`) stops new Pods landing there. Drain evicts the existing Pods (respecting PodDisruptionBudgets) — they get rescheduled on other Nodes. Pods that are `hostNetwork`/DaemonSet or lack a PDB get evicted anyway; `daemonset.maxUnavailable` controls how many roll at once.

## Storage

**Q7: What is the difference between `emptyDir`, `hostPath`, and a `PersistentVolume`?**
A: `emptyDir` = **ephemeral** storage tied to the Pod's life (gone on restart). `hostPath` = a directory on the **Node's filesystem** (survives Pod restart but NOT Node loss, and is node-locked). A `PersistentVolume` is a **cluster-managed** storage abstraction, usually backed by network storage (EBS/PD/NFS) — it decouples the Pod from where the data lives, so it survives both Pod and Node loss.

**Q8: How does a `StorageClass` enable dynamic provisioning?**
A: When you create a PVC that references a StorageClass (or the SC is the namespace default), the **in-tree/external controller** watches for unbound PVCs. It reads the StorageClass's `provisioner` (e.g., `ebs.csi.aws.com`, `pd.csi.google.com`) and `parameters` (size, type, fsType), **creates** the backing volume on the cloud/storage provider, then binds a fresh PV to the PVC — no manual PV needed.

## Security

**Q9: How does RBAC grant a Pod permission to read a ConfigMap?**
A: The Pod runs under a ServiceAccount. The API server checks whether a `Role`/`ClusterRole` with `get` on `configmaps` is bound to that SA (via `RoleBinding`/`ClusterBinding`) in that namespace. If yes, the request is allowed; if no, `403 Forbidden`. The binding's `subject` must reference the exact SA namespace/name.

**Q10: Are Kubernetes Secrets encrypted by default?**
A: **No.** Secrets are stored **base64-encoded** in etcd — that's encoding (trivially reversible), not encryption. If an attacker exfiltrates etcd, Secrets are readable plaintext. Encryption at rest (`EncryptionConfiguration` + `--encryption-provider-config` on the API server) is opt-in; otherwise a stolen etcd backup exposes the cluster's credentials.

## Networking

**Q11: How does a ClusterIP Service load-balance?**
A: The kubelet runs **kube-proxy** on each Node, which translates every Service (ClusterIP + endpoints) into **iptables/IPVS** rules. A SYN to the ClusterIP is **DNAT'd** (in `nat PREROUTING`/`OUTPUT`) to a random backing Pod IP. With IPVS it's a real LB algorithm (`rr`, `lc`, `wlc`); with iptables it's a probability-per-endpoint chain. There's no separate load-balancer VM unless you set `type: LoadBalancer`.

**Q12: Can a `hostNetwork: true` Pod and a CNI coexist?**
A: Yes — a host-network Pod **shares the host network namespace** (no CNI veth, `hostNetwork: true`), so it binds the host's ports directly. A separate CNI Pod gets a veth in a netns and a Pod IP. They share the Node's routing table, so don't bind the same port. Host-network is common for Ingress/controllers/DAemons that must bind host ports.

## Observability

**Q13: What is the difference between a metric and a log?**
A: A **metric** is an aggregated **numeric** time-series (e.g. `rate(errors[5m]) = 0.2/sec`) — lossy, queryable over windows, what you alert on. A **log** is a discrete **text/JSON event** (e.g. `ERROR connection refused to db:5432`) — lossless, you search/filter lines for debugging. Metrics tell you *something's wrong*; logs tell you *what*.

**Q14: What is a histogram, and why are histogram buckets important for alerts?**
A: A histogram buckets observations into ranges (`le` boundaries like 0.1s, 0.5s, 1s). With buckets you can compute **any quantile** in any window at query time, e.g. `histogram_quantile(0.99, rate(latency_bucket[5m]))`. Without a histogram (just an average/gauge), a 50th-percentile "looks fine" while your tail latency burns SLA.

## Service Mesh & Advanced

**Q15: What does a sidecar Envoy proxy actually intercept in service-to-service calls?**
A: With iptables redirection (or eBPF in Cilium), all `podIP:port` traffic is redirected to the sidecar (`127.0.0.1:15001`), so the app sends to `localhost` and the proxy does mutual TLS + routing + metrics transparently. The app sees plain HTTP on localhost; mTLS happens between proxies. Disable via the `SERVICE_MESH`... / `sidecar.istio.io/inject: "false"` annotation on the Pod.

**Q16: How does `kubectl apply` differ from `kubectl create`? What is the declarative model?**
A: `create` POSTs a new object (fails if it exists). `apply` does a **two-way merge**: it computes a patch between what you're sending, the last-applied annotation, and the live state — so it's idempotent and reconciles drift. Declarative means "state your desired end-state, let the controller converge"; imperative is "run this command." The exam uses `apply`/`replace` heavily because it's how controllers + GitOps work.

**Q17: What happens during a rolling update failure, and how do you recover?**
A: The Deployment controller applies the new ReplicaSet; old Pods are terminated as new ones become Ready (per `progressDeadlineSeconds`). If the new version never becomes healthy, the rollout **pauses** and the Deployment is marked `Progressing=False`. Recovery: `kubectl rollout undo deployment/<name>` (rollback to the prior ReplicaSet) — the new RS is scaled to 0, the old one back to full.

**Q18: What is the difference between a liveness and a readiness probe, and why use both?**
A: **Liveness** tells kubelet "this container is alive?" → if it fails, the container is **restarted**. **Readiness** tells the endpoints controller "should this Pod receive traffic?" → if it fails, the Pod is **removed from Service endpoints** (no new traffic), but kept running. Confusing them = restart storms (a slow warm-up fails liveness) or 502s (a dead Pod stays in endpoints).

**Q19: What is a PodDisruptionBudget, and what can you NOT prevent with it?**
A: A PDB sets `minAvailable`/`maxUnavailable` for voluntary disruptions (drain, upgrade, cluster autoscaler) — it stops the eviction API from taking down too many Pods at once. It does **nothing** for involuntary outages (Node dies, OOM-kill, Spot termination) — those bypass the PDB entirely.

**Q20: How does garbage collection of owned resources work?**
A: Controllers (ReplicaSet, Job, Deployment, etc.) set an **ownerReference** — a back-pointer to the owning controller. When the owner is deleted, the garbage collector either (foreground, `policy: Foreground`) deletes the children first then the owner, or (orphan / `Background`) deletes the owner then cascades to children. `kubectl delete --cascade=foreground|background|orphan` selects the strategy; orphaning leaves children dangling (they keep running, no owner).
