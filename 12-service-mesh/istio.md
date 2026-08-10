# Istio

> **Category:** Service Mesh

## What It Is

**Istio** is the most popular **service mesh**. It injects a **sidecar proxy (Envoy)** into each Pod and uses a **control plane (Istiod)** to manage traffic routing, mutual TLS, observability, and policy — all via Kubernetes CRDs.

## Why It Exists

- Secure service-to-service (**mTLS**) without app changes
- Fine-grained traffic control (canary, blue/green, retries, timeouts)
- Rich observability (metrics, traces, access logs via Envoy stats)
- Authorization (`AuthorizationPolicy`) at L3-L7

## Architecture (Istio 1.x)

```mermaid
graph TD
    A[App Pod\ncontainer + istio-proxy] --> B[Sidecar Envoy\ndata plane]
    C[Istiod\ncontrol plane\n(Pilot + Citadel + Galley)] --> B
    B --> D[App Pod 2 + Envoy]
    E[Istio Ingress Gateway\n(a Service + Deployment)] --> B
    F[External Client] --> E
    C --> C2[XDS API\nconfigures Envoys]
```

### Components

| Component | Role |
|-----------|------|
| **istiod** (Pilot) | Distributes service discovery + config (xDS) to Envoys |
| **istiod** (Citadel) | Identity + mTLS cert issuance (workload certificates) |
| **istiod** (Galley) | (Legacy) validates + processes config |
| **Envoy (istio-proxy)** | Sidecar data-plane proxy injected into each Pod |
| **Istio Ingress Gateway** | A specialized Envoy (Deployment + Service) at the cluster edge |

## Installation (Istioctl)

```bash
# Download istioctl (matches your K8s version)
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install + the demo profile (includes gateways, telemetry, istiod)
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled

# Verify
kubectl get pods -n istio-system
kubectl get svc -n istio-system     # istio-ingressgateway LoadBalancer IP
```

### Installation profiles

| Profile | What's included | Use |
|---------|-----------------|-----|
| `default` | istiod + ingress gateway (minimal) | Production baseline |
| `demo` | + telemetry, addons (Kiali, Prometheus, etc.) | Testing / demos |
| `minimal` | istiod only (no gateway) | Bare metal, custom ingress |
| `empty` | nothing — you enable components | Custom minimal deploy |

## Sidecar Injection

Automatic via a MutatingWebhookConfiguration — label the namespace:
```bash
kubectl label namespace my-ns istio-injection=enabled
# OR the newer label:
kubectl label namespace my-ns istio.io/rev=default
```

Verify a Pod has the sidecar:
```bash
kubectl get pod <name> -o jsonpath='{.spec.containers[*].name}'
# output includes: "istio-proxy"
```

## Core CRDs (Istio API)

| CRD | Purpose | Key API group |
|-----|---------|----------------|
| `Gateway` | Edge gateway + TLS listener rules | `networking.istio.io/v1beta1` |
| `VirtualService` | HTTP/L7 routing (hosts, paths, retries, timeouts) | `networking.istio.io/v1beta1` |
| `DestinationRule` | Subset / load-balancing / outlier detection for a `Service` | `networking.istio.io/v1beta1` |
| `ServiceEntry` | Import/reach external services into the mesh | `networking.istio.io` |
| `AuthorizationPolicy` | L3-L7 allow/deny + JWT | `security.istio.io/v1` |
| `RequestAuthentication` | Define JWT issuer for a service | `security.istio.io` |
| `EnvoyFilter` | Raw Envoy config patch (advanced) | `networking.istio.io/v1alpha3` |
| `Sidecar` | Scope which ingress/egress the sidecar receives | `networking.istio.io/v1beta1` |

## Traffic Management

### Gateway (edge listener)
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "my-app.example.com"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE             # Terminate TLS here (cert in a Secret)
      credentialName: my-tls
    hosts:
    - "my-app.example.com"
```

### VirtualService (routing)
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-vs
spec:
  hosts:
  - my-app.default.svc.cluster.local
  - my-app.example.com
  http:
  - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: my-app.default.svc.cluster.local
        subset: v1
    retries:
      attempts: 3
      perTryTimeout: 2s
    timeout: "5s"
  - route:                       # Catch-all
    - destination:
        host: my-app.default.svc.cluster.local
        subset: v2
```

### DestinationRule (subset + lb)
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-dr
spec:
  host: my-app.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN       # ROUND_ROBIN | LEAST_CONN | RANDOM
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
    outlierDetection:          # Circuit-breaking / ejecting bad hosts
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

## Security

### PeerAuthentication (mTLS mode)
```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default-mtls
  namespace: istio-system
spec:
  mtls:
    mode: STRICT            # DISABLE | PERMISSIVE | STRICT
```

### AuthorizationPolicy (L3-L7 allowlist)
```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: my-authz
  namespace: default
spec:
  selector:
    matchLabels:
      app: ratings
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/bookinfo-ratings"]  # Only this SA
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/ratings/*"]
  - {}      # Empty rule = allow (useful to open after a default-deny)
```

### RequestAuthentication (JWT)
```yaml
apiVersion: security.istio.io/v1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: my-api
  jwtRules:
  - issuer: "https://issuer.example.com"
    jwksUri: "https://issuer.example.com/keys"
  # A matching AuthorizationPolicy then allows 'requestPrincipals' to match.
```

## Observability & Addons (Demo profile)

```bash
# The demo profile ships addons in addon namespace:
kubectl get pods,svc -n istio-system -l istio=addons
# prometheus, grafana, kiali, grafana, prometheus, jaeger, ...

# Install addons manually (or use the demo ones from the istio repo):
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.22/samples/addons
```

### Kiali dashboard
```bash
kiali-dashboard port-forward:
kubectl port-forward -n istio-system svc/kiali 20001:20001
# Then: browser -> http://localhost:20001/kiali
# Shows: Service graph, mTLS status, outbound traffic, metrics.
```

### Prometheus metrics (what an Envoy emits on /stats)
- `istio_requests_total` — RPS by response code
- `istion_request_duration_seconds_bucket` — latency histogram
- `istio_tcp_connections_opened_total`
- `istio_requests_total{response_code="5xx"}` — error rate (alert!)

### Distributed tracing (Jaeger)
Requires the `RequestHeader` / a tracer plugin. Envoy emits spans to Jaeger/Tempmetry backend.

## Debugging mTLS / Traffic

```bash
# Is mTLS on?
istioctl authn tls-check <pod> <host>
# Expect: STRICT (mTLS required by DestinationRule/PeerAuth)

# View Envoy config on a Pod:
istioctl proxy-config listeners <pod>.<ns>
istioctl proxy-config clusters <pod>.<ns>
istioctl proxy-config routes <pod>.<ns>

# Check for config errors / proxy status:
istioctl proxy-status               # Are all Envoys in sync with Istiod?
kubectl describe pod <pod>           # Check the istio-proxy containers

# Traffic flow
istioctl experimental wait --for=distribution --timeout=30s

# Check AuthorizationPolicy effect:
kubectl exec <src-pod> -c istio-proxy -- curl -v http://<dst-svc>/
# 403 → the authz policy denied it.
```

## Common Issues

### Pods don't get a sidecar (no injection)
```bash
kubectl get pod <name> -o jsonpath='{.spec.containers[*].name}'
# Missing "istio-proxy" → the namespace isn't labeled
kubectl describe namespace <ns> | grep -i istio
```

### "RBAC: ... is forbidden" after enabling authz
```yaml
# Default = ALLOW ALL once an AuthorizationPolicy exists.
# If you add a DENY rule, you must add ALLOW rules (or an empty `rules: [{}]`).
# The first AuthorizationPolicy on a namespace flips it from "allow all" to "deny all by default"
```

### mTLS: 503 / connection reset
```bash
istioctl authn tls-check <src> <dst-host>
# Mismatch: PeerAuthentication=STRICT but the peer doesn't have certs (not injected).
# Fix: ensure both pods are in injected namespaces + the Gateway sidecars have certs.
```

### "no healthy upstream"
```yaml
# The DestinationRule subset name doesn't match the Pod labels.
# Or: the ServiceSelector doesn't target the Pods.
kubectl get endpoints <svc>       # Are there ready endpoints?
kubectl describe dr <name>
```

### Ingress gateway not receiving traffic
```bash
kubectl get svc -n istio-system istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress}'
# Use this EXTERNAL-IP. Check the Service + LoadBalancer + DNS.
kubectl describe gateway <name>
```

## Istioctl Cheatsheet

```bash
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
istioctl verify-install
istioctl proxy-config clusters <pod>.<ns>
istioctl proxy-config listeners <pod>.<ns>
istioctl proxy-config routes <pod>.<ns>
istioctl proxy-status                         # Envoy sync health
istioctl authn tls-check <pod> <host>
istioctl experimental analyze                  # Validate manifests pre-deploy
istioctl experimental wait --for=distribution --timeout=30s
```

## Istio vs Linkerd

| Feature | Istio | Linkerd |
|---------|-------|---------|
| Proxy | Envoy | linkerd-proxy (Rust) |
| mTLS | Yes (automatic) | Yes (automatic) |
| Traffic mgmt | Full (VS, DR, GW) | Basic (ServiceProfile) |
| Observability | Via Kiali/Prom | Via linkerd-viz |
| Footprint | Larger (Envoy + istiod) | Smaller |
| Learning curve | Steep | Gentle |
| CRDs | ~15 networking/security CRDs | Fewer |

## When to use Istio

- You need **advanced L7 routing** (canary, retries, timeouts, fault injection)
- You want **central mTLS** + **zero-trust** via AuthorizationPolicy
- You need **fine-grained** egress control

When NOT to: small teams, latency-sensitive apps (proxy hop), or if NetworkPolicies + a good ingress (NGINX/Traefik) suffice.

## Interview Questions

**Q: What is a sidecar proxy and how is it injected?**
A: The Envoy (`istio-proxy`) injected into each Pod via a MutatingWebhookConfiguration (triggered by a label on the namespace). The app talks to `localhost`; the proxy handles mTLS/routing/metrics.

**Q: What is the role of istiod?**
A: The Istio control plane — it (1) pushes config/routing to Envoys via xDS (Pilot), (2) issues mTLS certs (Citadel), and validates config (Galley). It is the brains; the sidecars are the muscle.

**Q: How does mTLS work in Istio?**
A: istiod's certs (SPIFFE SVIDs) are rotated into each Envoy. Envoys negotiate mTLS between themselves. The app sees plaintext on localhost. Modes: DISABLE, PERMISSIVE, STRICT (via PeerAuthentication).

**Q: What is a VirtualService vs DestinationRule?**
A: VirtualService = request **routing** (hosts, paths, matches, retries). DestinationRule = **connection-level** config for a destination (subsets, load-balancing, outlier detection, TLS settings).

**Q: What's a Gateway in Istio?**
A: A load balancer (often `istio-ingressgateway`) that configures which incoming traffic is allowed (ports, hosts, TLS) — and a config that binds VirtualServices to that gateway for edge routing.

**Q: What does AuthorizationPolicy control?**
A: L3-L7 allow/deny rules (who, from where, to which path/method/port). The **first** AuthorizationPolicy on a namespace flips the default from "allow all" to "deny all" — so you must add allow rules.

## Related Resources

- [Service Mesh Overview](service-mesh.md)
- [Linkerd](linkerd.md)
- [Ingress Controllers](../04-networking/ingress-controllers.md)
- [Network Policies](../04-networking/network-policies.md)
- [Security](../06-security/README.md)
