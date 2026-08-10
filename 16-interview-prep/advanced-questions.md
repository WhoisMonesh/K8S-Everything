# Advanced / System-Design Kubernetes Questions

> **Category:** Interview Preparation

These are the senior/architect-flavored questions — scaling a control plane, designing for availability, trade-offs. Each links back to the relevant docs for the "why".

## Control Plane Design

**Q1: Why would you run an HA (N+1) control plane, and how does etcd quorum work?**
A: HA means at least 3 control-plane Nodes running kube-apiserver (behind an external LB) + an **etcd cluster** (odd number of members = 1, 3, or 5) using **Raft consensus**. etcd quorum = `(N/2)+1` — so with 3 members you tolerate 1 failure, with 5 you tolerate 2. etcd writes fail if quorum is lost (no leader), which is why an even-membered etcd cluster is an anti-pattern. In a 5-master cluster, losing 2 masters = loss of quorum = API unavailable.

**Q2: How would you back up and restore etcd safely in production?**
A: Use `etcdctl snapshot save` from a member with the client certs (best from localhost on an etcd host) — *never* from `kubectl exec` into the static pod (certs may lack permissions). Store the snapshot off-cluster (S3/GCS). For restore, you either (a) restore to a new data-dir for a brand-new etcd cluster (the recommended disaster-recovery path; requires `--initial-cluster` and peer re-join), or (b) restore in place (only safe for a single-member dev cluster — loses the cluster identity). **Key gotcha:** `etcdctl snapshot restore` rewrites the data-dir, WAL, and snap files to match new member names/IDs.

**Q3: What is kube-apiserver aggregation, and when do you use it?**
A: The API server delegates `*/v1` to built-in handlers but can **aggregate** extra API groups via the **aggregator layer** (`kube-apiserver --requestheader-*`). A third-party **APIService** points at an extension apiserver (e.g., `metrics-server`, a CRD controller, or your custom resource server). It's used to extend K8s with new resources/typeservers without forking the core, and the kube-aggregator re-exports them as first-class API groups.

## Networking at Scale

**Q4: When would you move kube-proxy from iptables to IPVS mode, and what are the caveats?**
A: IPVS (Linux `ip_vs`) is a real L4 LB with O(1) lookups and more algorithms (wrr, lblc, dh, sh...). You move to IPVS when you exceed ~500–1000 Services and iptables chain length causes latency/slow syncs (`KUBE-SVC-*` chains run in the hundreds, each flush/rewrite is O(n)). Caveats: kernel must load `ip_vs*` modules, kube-proxy must run as `privileged: true` (or with the right `CAP_NET_ADMIN`), and debugging uses `ipvsadm -Ln` instead of `iptables -t nat -L`.

**Q5: How does a Kubernetes cluster connect to an on-prem/legacy network, and what are the gotchas?**
A: Typically: (a) a `Service` of `type: LoadBalancer` whose LB (NLB/NSX) routes to a firewall/NAT that advertises your on-prem prefixes, (b) or **BGP peering** from the CNI (Calico/Flannel/VXLAN) into the enterprise fabric, (c) or a **VPN** (OpenVPN/IPsec sidecar) for private links. Gotchas: Pod CIDR range overlaps your on-prem RFC1918, so you must translate (NAT) or pick non-overlapping CIDRs; MTU mismatches over the tunnel drop large packets; and the cloud LB must be told which Pods are `Ready` (readiness gates / external health checks).

## Storage at Scale

**Q6: What makes a PersistentVolume "ReadWriteMany" or "ReadOnlyMany", and which plugins support which?**
A: It's the PV's `accessModes`, declared by whoever creates the PV (or derived from the StorageClass). RWO = one Pod (any one node) *read-write*; RWX = many Pods across nodes, read-write; ROX = many Pods, read-only. `hostPath`/`local` volumes are **RWO only** (Node-bound). Network-attached (EBS, PD, Ceph RBD) → RWO. Shared-file (NFS, CephFS, GlusterFS) → RWX. Some CSI drivers advertise capabilities per-access-mode, and the `volumeBindingMode: WaitForFirstConsumer` on a StorageClass defers binding until a Pod schedules (so an RWX doesn't bind cross-region).

**Q7: How does CSI differ from in-tree volume plugins, and what does the driver consist of?**
A: In-tree plugins (the old `kubernetes.io/*` volumes) had their code **compiled into kubelet/ kube-controller-manager** — so a storage vendor had to get their driver merged into core Kubernetes, slowing releases. **CSI** is an out-of-process **gRPC** plugin: a vendor ships a `CSI driver` (node Plugin + Controller service) as a DaemonSet + Deployment. The kubelet calls `NodePublishVolume`/`NodeStageVolume`; the controller calls `CreateVolume`/`DeleteVolume`. The CSI **sidecar containers** (provisioner, attacher, resizer, snapshotter) wrap the driver's gRPC and translate to K8s API calls. Migrating to CSI is the long-term direction (in-tree plugins are being removed).

## Performance & Cost

**Q8: If Pod-to-Pod latency spikes but CPU looks fine, where do you look?**
A: (1) The **CNI/overlay MTU** — VXLAN adds 50 bytes; a 1500-byte Pod MTU on a 1500 underlay → fragmentation + retransmits. (2) **CPUThrottling** — `cpu.cfs_quota_us`/`period` throttling makes apps appear under-utilized yet slow (check `cpu.stat` for `nr_throttled_periods`). (3) **Service mesh sidecar** (Envoy warmup, thread-starvation). (4) **DNS latency** — if app does a sync DNS lookup per request and CoreDNS is overloaded. (5) **Node-local cache misses** for images (slow pulls). Check `istioctl experimental wait`... no — check `kubectl top pods`, `ss -tno` inside the Pod, and a tcpdump of the Pod for retransmits.

**Q9: How do you size a Kubernetes cluster right, and what does "overhead" mean?**
A: Reserve ~5–10% CPU + 5–10% memory per Node for the **system/kubelet** (`--system-reserved` / `--kube-reserved` in Kubelet config, not via a LimitRange). The **pod overhead** is the cost of the Pod itself. **Add-on overhead** is kube-proxy/CNI/calico per Node. The **control-plane overhead** is etcd + API server load. For sizing, monitor `container_memory_working_set_bytes` (real resident) vs the request, and watch `OOMKilled` Pods — if you're OOM-killing, you either over-packed (lower density) or have a leak. The CNCF `kube-bench` (CIS) and `kube-cost` are the usual tools.

**Q10: What is the "noisy neighbor" problem in Kubernetes, and how do you mitigate it?**
A: A `Burstable`/`BestEffort` Pod consumes Node CPU/Mem unfairly — CPU hogging (via the scheduler's fairness in CFS, or throttling) or memory-starving neighbors via OOM kill. Mitigations: set **Requests** (so Burstable pods get their fair share) and Limits (so no one can grab the whole node); use **QoS** tiers — `Guaranteed` Pods (request==limit) are killed *last*; pin **CPU Manager** (`static` policy) for guaranteed CPU; and use **resource quotas + LimitRanges** to cap namespaces. For cross-node fairness use the **scheduler's scoring** (`least-requested` default) and taint `node.kubernetes.io/` + dedicated Nodes.

## Security at Scale

**Q11: How would you implement zero-trust service identity between two Pods?**
A: Give every Pod a **ServiceAccount** (no more default-token). Issue **SPIFFE SVIDs** (mTLS certs) for each workload identity — either via **cert-manager** + a custom issuer, or via a **service mesh** (Istio Citadel, Linkerd identity). Enforce mTLS with a **PeerAuthentication** `STRICT` (or Linkerd default). Authorize with `AuthorizationPolicy`/NetworkPolicy that matches the **service account identity** (`principals: ["cluster.local/ns/x/sa/y"]`), never an IP. Rotate certs regularly (the mesh does this automatically).

**Q12: What is "supply chain security" in Kubernetes, and the SLSA angle?**
A: It's "can I trust this container image?" Layers: (1) **Build provenance** — reproducible builds + signed attestations (SLSA Level 3 = GitHub Actions `attestations`). (2) **Image signing** — `cosign sign` the digest → registry, verified by a policy controller (`cosign verify` in CI or `policy-controller` admission). (3) **Vulnerability scanning** — fail builds on CVEs (`grype`/`trivy`). (4) **Base-image attestation** — pin to digests (`distroless`, `scratch`); scan the base for CVEs. SLSA is Google/NIST framework mapping to *how hardened your build is*; cosign is the *signature*; Kyverno/Gatekeeper is the *admission*.

## Multi-Cluster

**Q13: What's a clean multi-cluster strategy, and when do you NOT need it?**
A: Multi-cluster = **disaster recovery** (active/passive), **geo-distribution** (latency), or **tenant isolation** (prod vs staging). Clean approaches: (a) **GitOps per-cluster** with a shared Argo CD app-of-apps (each cluster has its own ingress/DNS/CNI); (b) a **fleet** tool (Fleet, Cluster API, Flux `GitRepository` per cluster) for drifts. You DON'T need multi-cluster for failure domains *within* one region — that's what AZs + PDBs + topology-spread-constraints solve. The 80/20 rule: one cluster with multiple AZs handles 90% of availability unless you have legal/regulatory data-residency requirements.

**Q14: How do you avoid "split-brain" across clusters during a failover?**
A: A failover that moves traffic from cluster A → cluster B must ensure writes (or state) aren't lost/duplicated. The pattern: **quiesce writes** to A (drain, set ingress to `503`), wait for in-flight writes to drain (or accept the loss window), then promote B (lift the drain), update DNS/Globo. If you have a shared backend (RDS, S3, DynamoDB) that's straightforward. If state lives in-cluster (etcd), you must **restore the backup** into B first, then cut traffic — never run both clusters writing the same datastore.

## Cost & Sustainability

**Q15: How do you right-size requests/limits in production without destabilizing apps?**
A: (1) **Observe first**: scrape `container_cpu_usage_seconds_total` + `container_memory_working_set_bytes` (prometheus + `histogram_quantile`). Compute `request = p95` for CPU and `request = p50` + `limit = p99` for memory (avoid OOM). (2) **Guardrails**: use VPA in "recommend-only" mode to propose requests, or `kube-cost`/` Goldilocks` to recommend. (3) **Roll out gradually**: patch a few Deployments at a time, watch Prometheus for OOM-kills (memory) and throttling (CPU — `rate(container_cpu_cfs_throttled_periods_total)`). (4) **Never lower a limit below peak usage**, and never raise a request without re-checking scheduling headroom (`kubectl describe node | Allocatable`).

## Exam/Design Quick Reference

| Concept | See also |
|----------|----------|
| etcd quorum, RAFT | [etcd.md](../02-architecture/etcd.md) |
| kube-proxy IPVS vs iptables | [cni-kube-proxy.md](../04-networking/cni-kube-proxy.md) |
| PV access modes, CSI | [storage.md](../05-storage/storage.md), [persistent-volumes.md](../05-storage/persistent-volumes.md) |
| CPU throttling | [resources.md](../07-scheduling-autoscaling/resources.md) |
| mTLS / zero-trust identity | [service-mesh.md](../12-service-mesh/service-mesh.md), [istio.md](../12-service-mesh/istio.md) |
| Image signing / cosign | [security.md](../06-security/README.md) |
| Disaster recovery | [backup-restore.md](../08-cluster-operations/backup-restore.md) |
