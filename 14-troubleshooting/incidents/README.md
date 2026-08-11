# Real Company Incident Case Studies

> **Category:** Troubleshooting / Production Incidents

These are **stylized case studies** based on real-world Kubernetes incidents documented in public postmortems, incident reports, and engineering blogs. Each case follows a consistent template:

- **Timeline**: what happened and when
- **Root cause**: the technical failure
- **Fix**: what was done to recover
- **Prevention**: how to avoid it next time
- **Interview angle**: how to discuss it in interviews

## Incidents catalog

| File | Company | Theme | Severity |
|------|---------|-------|----------|
| [gitlab-orm-migration-outage.md](gitlab-orm-migration-outage.md) | GitLab | Breaking schema migration → deployment cascade | S1 |
| [github-alb-nlb-firewall.md](github-alb-nlb-firewall.md) | GitHub | ALB controller + firewall rule → API throttling | S1 |
| [spotify-istio-cert-rotation.md](spotify-istio-cert-rotation.md) | Spotify | mTLS cert rotation → 5xx cascade | S2 |
| [slack-coredns-cache-thrashing.md](slack-coredns-cache-thrashing.md) | Slack | CoreDNS cache config → OOM → SERVFAIL | S2 |
| [zalando-etcd-quorum-loss.md](zalando-etcd-quorum-loss.md) | Zalando | etcd quorum loss + botched restore | S0 |
| [roblox-cpu-throttling.md](roblox-cpu-throttling.md) | Roblox | Hard CPU limits → throttle under load | S2 |
| [capital-one-cni-network-partition.md](capital-one-cni-network-partition.md) | Capital One | CNI upgrade → cross-AZ network partition | S1 |
| [adidas-helm-hook-partial-rollback.md](adidas-helm-hook-partial-rollback.md) | Adidas | Helm hook orphaned resources | S2 |
| [netflix-chaos-cascade.md](netflix-chaos-cascade.md) | Netflix | Chaos experiment with insufficient controls | S2 |

## Common patterns across incidents

1. **No canary rollout** — changes applied cluster-wide without staging
2. **Missing monitoring** — no alerts on key metrics (quorum, throttle, cache, health)
3. **No rollback plan** — recovery steps untested or undocumented
4. **Blast radius uncontrolled** — chaos, migrations, or config changes hit everything at once
5. **Cert/config rotation without overlap** — old config expires before new config propagates

## Related

- [Disaster Cases](../disaster-cases.md) — fictional template incidents
- [Troubleshooting Encyclopedia](../troubleshooting-encyclopedia.md) — diagnostic reference
- [Exam Walkthrough](../../16-interview-prep/exam-walkthrough.md) — interview prep
