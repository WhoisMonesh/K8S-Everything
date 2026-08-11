# Real Company Incident Case Studies

> **Category:** Troubleshooting / Production Incidents

These are **stylized case studies** based on real-world Kubernetes incidents documented in public postmortems, incident reports, and engineering blogs. Each case follows a consistent template:

- **Timeline**: what happened and when
- **Root cause**: the technical failure
- **Fix**: what was done to recover
- **Prevention**: how to avoid it next time
- **Interview angle**: how to discuss it in interviews

## Incidents catalog

### Infrastructure & Networking

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [cloudflare-bgp-leak.md](cloudflare-bgp-leak.md) | Cloudflare | BGP route leak → global outage | S0 |
| [amazon-us-east-1-outage.md](amazon-us-east-1-outage.md) | Amazon | Network device failure → K8s control plane isolation | S0 |
| [google-cloud-config-push-outage.md](google-cloud-config-push-outage.md) | Google Cloud | Bad config push → service management failure | S0 |
| [azure-load-balancer-outage.md](azure-load-balancer-outage.md) | Microsoft Azure | LB config update → invalid health probe | S0 |

### Security & Compliance

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [tesla-k8s-dashboard-cryptojacking.md](tesla-k8s-dashboard-cryptojacking.md) | Tesla | Exposed K8s dashboard → cryptojacking | S1 |
| [stripe-cert-expiry.md](stripe-cert-expiry.md) | Stripe | TLS certificate expiry → API outage | S0 |
| [reddit-rbac-lockout.md](reddit-rbac-lockout.md) | Reddit | RBAC misconfiguration → admin lockout | S1 |
| [capital-one-breach.md](capital-one-breach.md) | Capital One | SSRF + IAM misconfiguration → data breach | S0 |

### Application & Performance

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [shopify-oom-kill-storm.md](shopify-oom-kill-storm.md) | Shopify | Memory leak → cascading OOM kills | S1 |
| [discord-memory-leak.md](discord-memory-leak.md) | Discord | Goroutine leak → pod restarts | S2 |
| [uber-cascading-failure.md](uber-cascading-failure.md) | Uber | Cascading failure across microservices | S1 |
| [airbnb-resource-exhaustion.md](airbnb-resource-exhaustion.md) | Airbnb | Resource quota exhaustion → scheduler starvation | S2 |
| [roblox-hpa-misconfiguration.md](roblox-hpa-misconfiguration.md) | Roblox | HPA misconfiguration → scaling oscillation | S2 |

### Storage & Data

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [wayfair-storage-failure.md](wayfair-storage-failure.md) | Wayfair | StorageClass deletion → PVC binding failures | S1 |
| [adidas-pvc-binding-failure.md](adidas-pvc-binding-failure.md) | Adidas | StorageClass quota exhaustion → PVC pending | S2 |

### Package Management & Configuration

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [goldman-sachs-helm-conflict.md](goldman-sachs-helm-conflict.md) | Goldman Sachs | Helm version conflict → release stuck | S2 |
| [gitlab-helm-corruption.md](gitlab-helm-corruption.md) | GitLab | Corrupted Helm chart → release FAILED | S2 |
| [spotify-configmap-corruption.md](spotify-configmap-corruption.md) | Spotify | Invalid YAML in ConfigMap → pod crash-loop | S2 |

### Networking & Service Mesh

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [linkedin-dns-outage.md](linkedin-dns-outage.md) | LinkedIn | DNS zone file corruption → service discovery failure | S1 |
| [twilio-dependency-failure.md](twilio-dependency-failure.md) | Twilio | External DNS provider outage → no fallback | S1 |
| [slack-service-mesh-outage.md](slack-service-mesh-outage.md) | Slack | Istio strict mTLS → non-Istio pods blocked | S1 |

### Infrastructure & Operators

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [pinterest-node-failure-storm.md](pinterest-node-failure-storm.md) | Pinterest | Network switch failure → 20 nodes unreachable | S1 |
| [bloomberg-api-server-overload.md](bloomberg-api-server-overload.md) | Bloomberg | Watch storm → API server CPU 100% | S1 |
| [zalando-operator-crash-loop.md](zalando-operator-crash-loop.md) | Zalando | API change → operator crash-loop | S1 |
| [jpmorgan-network-policy.md](jpmorgan-network-policy.md) | JPMorgan | NetworkPolicy blocking all ingress | S1 |

### Capacity & Scaling

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [epic-games-fortnite-outage.md](epic-games-fortnite-outage.md) | Epic Games | Traffic surge → GKE capacity exhaustion | S0 |
| [apple-icloud-outage.md](apple-icloud-outage.md) | Apple | Bad config push → service mesh failure | S2 |
| [gitlab-database-incident.md](gitlab-database-incident.md) | GitLab | Accidental database deletion → data loss | S0 |

### Chaos Engineering

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [netflix-chaos-gone-wrong.md](netflix-chaos-gone-wrong.md) | Netflix | Chaos experiment with insufficient controls | S2 |

## Common patterns across incidents

1. **No canary rollout** — changes applied cluster-wide without staging
2. **Missing monitoring** — no alerts on key metrics (quorum, throttle, cache, health)
3. **No rollback plan** — recovery steps untested or undocumented
4. **Blast radius uncontrolled** — chaos, migrations, or config changes hit everything at once
5. **Cert/config rotation without overlap** — old config expires before new config propagates
6. **Insufficient access controls** — excessive IAM permissions, exposed dashboards
7. **No dependency redundancy** — single point of failure in external services
8. **Configuration drift** — manual changes without GitOps or PR review

## Related

- [Disaster Cases](../disaster-cases.md) — fictional template incidents
- [Troubleshooting Encyclopedia](../troubleshooting-encyclopedia.md) — diagnostic reference
- [Exam Walkthrough](../../16-interview-prep/exam-walkthrough.md) — interview prep
