# Linkerd

> **Category:** Service Mesh

## What It Is

**Linkerd** is a lightweight, **opinionated service mesh** for Kubernetes. Like Istio, it injects a sidecar proxy that handles **mTLS, metrics, and traffic policy** — but with a smaller footprint, a simpler installation, and fewer CRDs, so it's easier to adopt.

## Why Use Linkerd

- Easy install (`linkerd install | kubectl apply -f -`, then `linkerd check`)
- Automatic, zero-config **mTLS** between Pods in a mesh
- Good-enough **traffic metrics** (success rate, RPS, latency) out of the box
- Small, Rust-based proxy (no Envoy memory overhead per Pod)
- Simpler security/trust model than Istio — less policy to misconfigure

## Architecture

```mermaid
graph TD
    subgraph "Control plane (linkerd)"
        A[linkerd-identity\n(issuing certs)]
        B[linkerd-proxy-inject\n(webhook for injection)]
        C[linkerd-policy\n(policy controller)]
        D[linkerd-destination\n(service discovery)]
        E[linkerd-heartbeat\n(check-ins)]
    end
    subgraph Data plane
        F[Pod A\napp + linkerd-proxy] --> G[linkerd-proxy]
        H[Pod B\napp + linkerd-proxy] --> I[linkerd-proxy]
    end
    G <--> I
    A --> G
    A --> I
    B --> F
    B --> H
    D --> G
    D --> I
```

- The **proxy** (`linkerd-proxy`, a Rust binary) is injected into each Pod. It enforces mTLS and emits metrics.
- The **control plane** is installed in the `linkerd` namespace: `identity` (cert issuance), `proxy-inject` (webhook for auto-injection), `destination` (service discovery + endpoint resolution), `policy` (auth policy).
- Linkerd proxy uses **HTTP/2 via TCP** for mesh traffic and speaks a **simple protocol** (not full Envoy xDS), which is why it's lighter.

## Installation

```bash
# Install the CLI (matches your Linkerd version):
curl -sL https://run.linkerd.io/install | sh
export PATH=$PATH:$HOME/.linkerd2/bin

# Install the control plane:
linkerd install | kubectl apply -f -
# Annotate the namespace to enable injection + proxy config:
linkerd inject --prune -f my-manifest.yaml | kubectl apply -f -
# OR annotate a live namespace:
kubectl annotate namespace my-ns linkerd.io/inject=enabled

# Verify everything's green:
linkerd check
linkerd identity            # check trust anchors (root certs)
```

### Versions (and the v3 / multi-cluster story)

- **Linkerd 2.x** — the widely adopted single-cluster mesh (the focus here).
- **Linkerd 3.0+** — upcoming; designed around **gateway-api**, multi-cluster first, pluggable proxy (envoy vs. custom). Still maturing.
- **Linkerd multi-cluster** (`linkerd multicluster`) — installs a `mirror` service in the destination cluster so cross-cluster traffic is mTLS'd too.

### Control-plane components (Linkerd 2)

| Component | Role |
|-----------|------|
| `linkerd-identity` | Workload cert (SVID) issuance + trust anchor distribution |
| `linkerd-proxy-inject` | Webhook that adds `linkerd-proxy` to Pods |
| `linkerd-destination` | gRPC server for service discovery (endpoints by hostname) |
| `linkerd-policy` | Enforces authorization policy (K8s-native) |
| `linkerd-heartbeat` | Periodic liveness / stats check |

## Trust & mTLS

Linkerd has one **trust anchor** (root CA) per cluster. Workload certs are issued off it.

### Trust anchor rotation (without downtime)

```bash
# Generate a fresh trust anchor + Issuer (or use step / cert-manager):
step certificate create identity.linkerd.cluster.local \
  ca.crt ca.key --profile custom --not-after 8760h --crv ECDSA
# Or: use `linkerd trust anchor add` (CLI helper) — re-encrypts the Issuer.
linkerd install --identity-trust-anchors-file=ca.crt --identity-issuer-cert-file=iss.crt --identity-issuer-key-file=iss.key | kubectl apply -f -
linkerd check
```

The proxy certs **rotate every ~24h** automatically — the proxy fetches a fresh cert from `linkerd-identity` (over a secure channel) before the current one expires.

## Authorization Policy (Linkerd 2.14+)

Linkerd now ships a **policy** controller (K8s-native `AuthorizationPolicy`, `Server`, `HTTPRoute`).

```yaml
apiVersion: policy.linkerd.io/v1alpha1
kind: Server
metadata:
  name: my-server
  namespace: default
spec:
  podSelector:
    app: my-app
  port:
    port: http
    protocol: opaque      # or http, http2
---
apiVersion: policy.linkerd.io/v1alpha1
kind: AuthorizationPolicy
metadata:
  name: my-authz
  namespace: default
spec:
  targetRef:
    kind: Server
    name: my-server
  # Empty = ALLOW ALL authenticated (mTLS'd) traffic.
  # Add `rules` to restrict:
  rules:
  - from:
    - kind: ServiceAccount
      name: frontend
      namespace: default
    # to: (optional — restrict by path in newer versions)
```

| Policy kind | Meaning |
|-------------|---------|
| `Server` | A named Pod selector + port (the "surface" to protect) |
| `AuthorizationPolicy` | Allow/deny rules (who can talk to the Server) |
| `HTTPRoute` | L7 routing (via Gateway API) |
| `MeshService` | Marks a service as part of the mesh (mTLS on) |

## Traffic Management

Linkerd's traffic management is intentionally **simple** (compare to Istio's full VirtualService/DR). It centers on:

- **`ServiceProfile`** — per-route metrics + retry policy
- **`HTTPRoute`** (Gateway API) — L7 routing (in v2.14+)
- **`TrafficSplit`** — for canary / A/B, usually via an add-on (Flagger)

### ServiceProfile (the classic Linkerd traffic tool)

```yaml
apiVersion: split.smi.k8s.io/v1beta1
kind: TrafficSplit           # SMI CRD alternative (if using the SMI plugin)
...
---
apiVersion: linkerd.io/2.14
kind: ServiceProfile
metadata:
  name: web-svc.my.svc.cluster.local    # <svc>.<ns>.svc...
  namespace: my-app
spec:
  routes:
  - name: /api/v1  # a route (path or regex)
    condition:
      type: PathPrefix
      value: /api/v1
  # Then: retry / timeout policies attach to a route.
```

### TrafficSplit + Flagger (canary)

```bash
# Install Flagger with Linkerd as the provider:
helm install flagger flagger-app/flagger \
  --namespace=linkerd \
  --set meshProvider=linkerd \
  --set metricsServer=http://linkerd-prometheus:9090
# Canary on an existing Deployment + Service:
kubectl apply -f canary.yaml
```

## Observability (linkerd-viz)

```bash
# Install the viz extension (metrics + dashboard):
linkerd viz install | kubectl apply -f -
linkerd check

# Live request stream (tap):
linkerd viz tap deployment/my-app -n my-ns

# Stats (RPS / success / latency):
linkerd viz stat deployment -n my-ns
linkerd viz stat outbound -n my-ns svc/my-svc

# Topology:
linkerd viz edges deployment -n my-ns     # who talks to whom

# Open the dashboard:
linkerd viz dashboard
```

Metrics you get by default:

- `server_request_total` (RPS by response class)
- `server_request_duration_seconds` (latency buckets)
- `stream_tcp_open_total` (TCP connections)
- `proxy_memory / proxy_cpu` (proxy resource usage)

These are scraped by `linkerd-prometheus`, then visualized by `linkerd-grafana`.

## CLI Cheatsheet

```bash
linkerd check                     # cluster-wide mesh health
linkerd install | kubectl apply -f -     # install control plane
kubectl annotate namespace ns linkerd.io/inject=enabled
linkerd inject -f deploy.yaml | kubectl apply -f -   # inject a manifest
linkerd viz stat deploy -n ns     # per-deployment success/latency
linkerd viz tap deploy -n ns      # live requests
linkerd viz dashboard             # open UI
linkerd identity                  # check trust anchor / certs
linkerd multicluster install ...  # multi-cluster (separate)
```

## Debugging

```bash
# Proxy not injected?
kubectl get pod my-pod -o jsonpath='{.spec.containers[*].name}'
# Missing "linkerd-proxy" → namespace isn't annotated, or the webhook is down:
kubectl get mutatingwebhookconfiguration linkerd-proxy-injector

# mTLS failures / "connection refused"?
linkerd viz check --proxy
# Look at the proxy log:
kubectl logs my-pod -c linkerd-proxy
kubectl port-forward <pod> 4190 # → http://localhost:4190/metrics (Prometheus format)
kubectl port-forward <pod> 4191 # → http://localhost:4191/ready

# Authz policy not working?
linkerd check --proxy
kubectl describe authzpolicy my-authz
linkerd viz stat outbound -n ns      # is traffic actually flowing?
```

## Common Issues

### "identity not ready" / cert rotation failures
- The trust anchor in the cluster is expiring. Run `linkerd identity` and check `linkerd check`.
- Re-issue / rotate the anchor (see above) before the cert expires.

### Metrics missing / "no such metric"
- You must install `linkerd-viz` — base Linkerd does not ship a metrics stack.
- A `ServiceProfile` must exist for the route to show per-path metrics.

### AuthorizationPolicy silently denies everything
- An empty `AuthorizationPolicy` (no `rules`) = **deny all**. Add at least one rule or an empty allow (`{}`) to open it.

### Cross-cluster / egress traffic fails mTLS
- Linkerd mTLPs traffic between in-mesh Pods. External/egress traffic is **opaque** (not HTTP-routed) unless the protocol is recognized. Mark a service as `opaque` only when needed.

## Interview Questions

**Q: How does Linkerd differ from Istio?**
A: Linkerd is **lighter and simpler**: it's opinionated, ships with mTLS on by default, has fewer CRDs, and a smaller Rust proxy (not Envoy) → lower CPU/memory. Istio is more feature-rich (full traffic mgmt, Gateway API, extensibility) but heavier and more complex to tune.

**Q: How does mTLS work in Linkerd?**
A: The `linkerd-identity` control plane issues short-lived TLS certs (SPIFFE-style SVIDs) to each workload's proxy. Proxies automatically negotiate mTLS. No app change — traffic between two in-mesh Pods is encrypted and mutually authenticated by default.

**Q: What is a trust anchor, and why rotate it?**
A: The trust anchor is the cluster-wide root CA that signs workload certs. It must be valid for the proxies and control plane to trust each other. Rotating it (with rollover) prevents outages when the anchor nears expiry.

**Q: What does `linkerd inject` do?**
A: It mutates a manifest to add the `linkerd-proxy` sidecar, the `linkerd-init` (iptables redirect) init container, and required env vars/annotations — so the app's traffic flows through the proxy.

**Q: How do you debug a failing mesh?**
A: `linkerd check` (and `linkerd check --proxy`) shows component + proxy health. `kubectl logs <pod> -c linkerd-proxy` shows proxy logs, and `linkerd viz tap` shows live traffic — together they reveal whether mTLS, authz, or routing is the problem.

## When NOT to use Linkerd

- You need complex traffic routing that only Gateway API or Istio-style VirtualServices provide.
- You require deep integration with existing Envoy stacks / Istio tooling.
- You need first-class multi-cluster in a single mesh — Linkerd v2's multicluster is a separate add-on (v3 makes it native).

## Related Resources

- [Service Mesh Overview](service-mesh.md)
- [Istio](istio.md)
- [Linkerd docs](https://linkerd.io/docs/)
- [Gateway API / HTTP Routes](../04-networking/ingress.md)
- [Network Policies](../04-networking/network-policies.md)
- [Security](../06-security/README.md)
