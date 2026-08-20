# Prometheus

> **Category:** Observability / Monitoring

## What It Is

**Prometheus** is the standard **metrics** engine for Kubernetes. It's a **pull-based** time-series database with PromQL for queries, a simple HTTP data model, and a built-in alerting rule engine. In Kubernetes, the de-facto deployment is the **Prometheus Operator** (now the kube-prometheus-stack), which manages Prometheus instances declaratively.

## Why It Matters

- **Declarative** scrape config via `ServiceMonitor` / `PodMonitor` CRDs (no manual `--config.file`).
- **Kubernetes-native** alerting via `PrometheusRule` (rules-as-code, GitOps-able).
- Pull model (Prometheus scrapes you) makes **blackbox probing** easy (synthetic checks).
- Tight **Grafana** integration — dashboards are native to this stack.

## Architecture

```mermaid
graph TD
    subgraph "control plane"
        OPO[Prometheus Operator /<br/>Admission Webhooks]
        OPO --> PM
    end
    subgraph "Data" Plane "K8s cluster"
        A[App Service] --> B[Service<br/>has Pod]
        C[ServiceMonitor<br/>points at Service]
        C --> D[Prometheus<br/>scrapes pods]
        E[PrometheusRule<br/>alert rules] --> D
        D --> D2[Prometheus TSDB<br/>local on PVC]
        D --> F[Grafana<br/>queries via HTTP]
        D --> G[Alertmanager<br/>routes alerts]
        D --> H[long term<br/>storage e.g. VictoriaMetrics/S3]
    end
```

### The Operator's job
The **Prometheus Operator** watches for `Prometheus` CRs and, for each one:
- creates a **ConfigMap** with scrape config derived from your `ServiceMonitor`s/`PodMonitor`s,
- renders a **StatefulSet** for Prometheus with that config,
- ensures a **Service + ServiceMonitor** exists to scrape Prometheus itself,
- provisions a **PVC** (`storage:`) for the TSDB.

## Installation (kube-prometheus-stack)

The community "blessed" path is the **kube-prometheus** manifest + the **kube-prometheus-stack** Helm chart (Prometheus Operator + kube-state-metrics + node-exporter + Grafana + some alerts).

```bash
# Helm (recommended for custom installs):
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.enabled=true \
  --set alertmanager.enabled=true \
  --set alertmanager.config.global.slack_api_url="..." \
  --set kubeStateMetrics.enabled=true
```

> The chart ships: Prometheus Operator, Prometheus, Alertmanager, kube-state-metrics, node-exporter, and several "recorder" rulesets (so your dashboards work out of the box).

## Core CRDs (Prometheus Operator API)

| Resource | What it does |
|----------|--------------|
| `Prometheus` | A Prometheus instance (version, retention, resources, storage, scrape interval) |
| `ServiceMonitor` | "Scrape the pods backing this Service" — the declarative scrape target |
| `PodMonitor` | Like `ServiceMonitor`, but points at a Pod directly (no Service required) |
| `Probe` | Blackbox probe (HTTP/TCP) target set |
| `PrometheusRule` | Alert + recording rules, namespaced (the Operator bundles them into the Prometheus instance) |
| `AlertmanagerConfig` | Per-namespace routing/muting for Alertmanager |

### ServiceMonitor — scrape by Service
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  labels:
    release: kube-prometheus-stack    # match this in the Prometheus `serviceMonitorSelector`
spec:
  selector:           # which Service to scrape
    matchLabels:
      app: my-app
  namespaceSelector:
    any: false        # restrict to this namespace (or `any: true`)
  endpoints:
  - port: http        # the Service port name `name=http`
    path: /metrics
    interval: 30s
    relabelings:
    - sourceLabels: [__meta_kubernetes_pod_node_name]
      targetLabel: nodename
```

### PrometheusRule — alerts + recording rules
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: my-app-alerts
  namespace: monitoring
  labels:
    prometheus: kube-prometheus-stack-prometheus
    role: alert-rules
spec:
  groups:
  - name: my-app
    rules:
    - alert: HighErrorRate
      expr: |
        rate(http_requests_total{job="my-app",code=~"5.."}[5m])
        /
        rate(http_requests_total{job="my-app"}[5m]) > 0.05
      for: 2m            # fire only if sustained for 2m
      labels:
        severity: critical
      annotations:
        summary: "High 5xx error rate on {{ $labels.job }}"
        description: "{{ $value | humanizePercentage }} of requests are 5xx."
    - alert: PodCrashLooping
      expr: kube_pod_status_ready{condition="true"} == 0
      for: 5m
      labels:
        severity: warning
```

## Writing Good Alerts

| Bad | Good |
|-----|------|
| `up == 0` (host down) | `up == 0` *and* "is this impacting users" (down for >5m) |
| `node_cpu_seconds_total idle < 10` | Latency p99 > 1s (symptom, not cause) |
| `container_memory_usage_bytes > 90%` | `kube_pod_container_status_restarts_total` rising (the OOM is a symptom) |
| Too many alerts | Use `for:` + grouping + inhibit rules |

### The `for:` clause
This is the most important thing beginners miss:

```yaml
- alert: HighCpu
  expr: (1 - avg rate(node_cpu_seconds_total{mode="idle"}[5m])) by(node) > 0.95
  for: 5m     # don't alert until the condition holds for 5 minutes
```

Without `for:`, you get alerts on every single scrape — flapping, noisy, useless.

## PromQL Essentials

### Selectors and aggregations
```promql
# Rate of requests, grouped:
sum by(path) (rate(http_requests_total[5m]))

# Excluding a label (remove `instance`, keep `job`):
sum without(instance) (rate(http_requests_total[5m]))

# Count of healthy Pods per Deployment:
sum(kube_deployment_status_replicas{condition="available"})
```

### Histograms + quantiles
```promql
# p99 latency over 5m (requires `histogram_quantile` + a histogram metric):
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# p99 without `histogram_quantile` (use the built-in quantile over raw samples):
quantile(0.99, rate(grpc_server_handling_seconds_sum[5m]) / rate(grpc_server_handling_seconds_count[5m]))
```

### Joins and `ignoring`/`on`
```promql
# Rate of CPU per Pod (two vectors, join on `pod`):
rate(container_cpu_usage_seconds_total[5m])
and on (pod) kube_pod_info{node=~".+"}
```

## Storage & Retention

| Concept | Detail |
|---------|--------|
| Local TSDB | Prometheus stores blocks in `<storage>/prometheus` (PVC). Retention by time (default 10d) or size (`retention.size`). |
| Downsampling | Thanos/Cortex/VictoriaMetrics add long-term storage + compaction. |
| WAL | Write-ahead log for durability — survives restarts. |
| `--storage.tsdb.retention.time` | e.g., `30d`. Prefer size-based (`retention.size=50GB`) to avoid surprises. |

### Prometheus resource sizing
- TSDB grows ~1-2 GB per node per month depending on cardinality.
- High-cardinality metrics (user IDs as labels) can balloon storage — avoid them.

## Alertmanager

Alertmanager takes alerts from Prometheus (`alertmanager.url`), deduplicates, groups, routes, and inhibits them.

```yaml
# Example config (via `alertmanager.config` in the Helm chart or a Secret):
global:
  resolve_timeout: 5m
  slack_api_url: https://hooks.slack.com/services/...
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 10m
  repeat_interval: 3h
  receiver: 'slack'
  routes:
  - matchers:
    - severity =~ "critical|page"
    receiver: pagerduty
receivers:
- name: slack
  slack_configs:
  - channel: '#alerts'
- name: pagerduty
  pagerduty_configs:
  - service_key: '<key>'
```

## Probing (Blackbox)

Use a `Probe` to hit a URL/TCP port (e.g., your ingress) and measure up/correctness from *outside*:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Probe
metadata:
  name: ingress-check
  namespace: monitoring
spec:
  jobName: probe-ingress
  prober:              # the blackbox exporter
    url: prometheus-blackbox-exporter.monitoring.svc:9115
  targets:
    ingress:
      namespace: default
      matchLabels: {app: ingress-nginx}
  modules: [http_2xx]
```

Prometheus also ships a built-in `blackbox_exporter` via the chart (`extraScrapeConfigs`).

## kube-state-metrics (KSM)

KSM exposes Kubernetes object state as Prometheus metrics — no app instrumentation required:

| Metric family | Meaning |
|---------------|---------|
| `kube_pod_status_ready` | Pod ready=1/0 (per `condition`) |
| `kube_deployment_status_replicas` | Current/available/updated replicas |
| `kube_node_status_condition` | Node Ready + memory pressure |
| `kube_pod_container_status_restarts_total` | Pod restarts (OOM, crash) |
| `kube_service_spec_type` | Service type (ClusterIP, LoadBalancer, NodePort) |

```yaml
# Typical alert: Deployment not at desired replica count
- alert: DeploymentReplicasMismatch
  expr: kube_deployment_status_replicas{condition="available"}
        != kube_deployment_status_replicas{condition="updated"}
```

## Common Issues

### "I deployed a Service but Prometheus doesn't scrape it"
- Check the `ServiceMonitor` `selector.matchLabels` matches the Service's labels — **label name and value must match**.
- Check the `serviceMonitorSelector` on your `Prometheus` object (the chart's default `prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues` must let your labels through).
- The Service `port` needs a name (`name: http`) that the `ServiceMonitor.endpoints[].port` references.

### "My alert rule doesn't fire"
- `expr` typo → Prometheus rejects it. Check `kubectl describe prometheusrule` + Prometheus UI (`Status → Rules`).
- `for:` too short or missing → flapping. Add `for: 2m`.
- The rule's `groups`/`labels` don't match the `Prometheus` object's selector → the Operator doesn't load it.

### "Prometheus disk full"
- Lower retention, or add a `remoteWrite` to offload to long-term storage.
- Watch cardinality — `rate(my_counter_total[5m])` is fine; `my_counter_total{user_id=~".+"}` can explode.

### `kube-state-metrics` missing data after K8s upgrade
- KSM version must track your cluster version. Use the chart's pinned image.
- Some metrics are **opt-in** (e.g., `KUBE_CONTROLLER_CHART` or `--enable-collect-*` flags) — check the chart's `metric` overrides.

## Debugging Cheatsheet

```bash
# Which targets is Prometheus scraping, and their status?
PROM=$(kubectl get svc -n monitoring -l app.kubernetes.io/name=prometheus -o name)
kubectl -n monitoring port-forward $PROM 9090
open http://localhost:9090/targets

# Inspect a rule group:
open http://localhost:9090/alerts
open http://localhost:9090/graph?g0.expr=up

# Does the Alertmanager know the route?
kubectl -n monitoring port-forward alertmanager-main 9093
open http://localhost:9093/#/alerts

# Query via kubectl (useful for sanity):
kubectl exec deploy/prometheus -n monitoring -- \
  /bin/prometheus query 'up{job="kube-state-metrics"}'

# List all CRD instances:
kubectl get servicemonitors
kubectl get prometheusrules
kubectl get probe
```

## Interview Questions

**Q: Why is Prometheus "pull" rather than "push", and is that a problem?**
A: Pull lets Prometheus scrape at a known cadence, retry failed scrapes, and do blackbox probing without app cooperation. The downside is firewalling inbound scrape ports / handling dynamic targets — which `ServiceMonitor`s solve (the Operator reconciles them into config). Short-lived Jobs need a push gateway if their lifetime < scrape interval.

**Q: What is a ServiceMonitor in the Prometheus Operator?**
A: A CRD describing "scrape everything backing this Service, on this port/path". The Operator turns `ServiceMonitor`s into Prometheus scrape config — so you manage targets via GitOps instead of editing a config file.

**Q: What's the difference between a recording rule and an alert rule?**
A: A recording rule precomputes an aggregated series (e.g., `job:request_rate:5m`) and stores it back in the DB — faster queries + lower cardinality. An alert rule is like a recording rule but fires a notification to Alertmanager when its `expr` is true for `for:` duration.

**Q: Why is cardinality dangerous in Prometheus?**
A: Each unique label-set is a separate time series. Putting unbounded labels like `user_id`, `request_id`, or `path` (with high-cardinality paths) creates millions of series → OOM, slow queries, huge disk. Keep labels to bounded dimensions (job, namespace, code).

**Q: What is `kube-state-metrics`, and why do you need it?**
A: It translates Kubernetes object *state* into metrics (replicas available, Pod ready, restarts, node Ready) that you can alert on. Prometheus alone scrapes *app* + *kubelet* metrics — but not "how many Deployments are down?" That's KSM's job.

**Q: How do you alert that a Deployment is down?**
A: `kube_deployment_status_replicas{condition="available"} == 0` (with a `for:`), or the negative of `kube_deployment_status_replicas_available`. You can also check Pod readiness: `kube_pod_status_ready{condition="true"} == 0`.

## Related Resources

- [Monitoring Fundamentals](monitoring-fundamentals.md)
- [Grafana](grafana.md)
- [Alerting / Alertmanager](grafana.md) (Grafana Alerting + Alertmanager config)
- [Helm](../10-package-management/helm.md)
