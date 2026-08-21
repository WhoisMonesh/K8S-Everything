# Prometheus vs Datadog vs New Relic vs Grafana Cloud

> **Category:** Observability / Comparisons
> Decision guide for Kubernetes monitoring solutions.

## Overview

| Feature | Prometheus | Datadog | New Relic | Grafana Cloud |
|---------|------------|---------|-----------|---------------|
| **Type** | OSS | SaaS | SaaS | SaaS + OSS |
| **Metrics** | Yes | Yes | Yes | Yes |
| **Logs** | No (Loki) | Yes | Yes | Yes (Loki) |
| **Traces** | No (Tempo) | Yes | Yes | Yes (Tempo) |
| **APM** | No | Yes | Yes | Yes |
| **Alerts** | Yes | Yes | Yes | Yes |
| **Dashboards** | Grafana | Built-in | Built-in | Grafana |
| **Cost** | Free | $$$ | $$ | Free tier + $$ |
| **Complexity** | Medium | Low | Low | Medium |

## When to Use What

### Use Prometheus When:

- You want **open source** and **no vendor lock-in**
- You need **on-premise** monitoring
- You want **Grafana** dashboards
- You have **budget constraints**

```yaml
# Example: Prometheus deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        args:
        - '--config.file=/etc/prometheus/prometheus.yml'
        - '--storage.tsdb.retention.time=30d'
        ports:
        - containerPort: 9090
```

### Use Datadog When:

- You want **all-in-one** solution (metrics, logs, traces)
- You need **APM** out of the box
- You want **minimal setup**
- You have **budget** for SaaS

```bash
# Example: Install Datadog agent
helm install datadog datadog/datadog \
  --set datadog.apiKey=<YOUR_API_KEY> \
  --set datadog.site=datadoghq.com \
  --set targets=prometheus
```

### Use New Relic When:

- You want **full-stack observability**
- You need **free tier** for small deployments
- You want **NRQL** query language
- You need **errors inbox** for error tracking

```bash
# Example: Install New Relic agent
kubectl apply -f https://raw.githubusercontent.com/newrelic/infrastructure-agent/master/k8s/newrelic-infra.yml
```

### Use Grafana Cloud When:

- You want **Prometheus + Loki + Tempo** stack
- You need **free tier** with generous limits
- You want **Grafana** dashboards
- You prefer **open source** tools

```bash
# Example: Install Grafana Agent
helm install grafana-agent grafana/grafana-agent \
  --set config.cloudGestureURL=<YOUR_CLOUD_URL>
```

## Comparison Matrix

| Criteria | Prometheus | Datadog | New Relic | Grafana Cloud |
|----------|------------|---------|-----------|---------------|
| **Metrics storage** | Local/Remote | SaaS | SaaS | SaaS |
| **Query language** | PromQL | Datadog QL | NRQL | PromQL |
| **Dashboards** | Grafana | Built-in | Built-in | Grafana |
| **Alerting** | Alertmanager | Built-in | Built-in | Built-in |
| **Log aggregation** | Loki (separate) | Built-in | Built-in | Loki (separate) |
| **Distributed tracing** | Tempo (separate) | Built-in | Built-in | Tempo (separate) |
| **Service map** | No | Yes | Yes | Yes |
| **APM** | No | Yes | Yes | Yes |
| **Cost model** | Self-hosted | Per host | Per GB | Free + usage |

## Pricing Comparison

| Solution | Free Tier | Paid Plans |
|----------|-----------|------------|
| **Prometheus** | Unlimited (self-hosted) | N/A (OSS) |
| **Datadog** | 14-day trial | $15/host/mo (Infrastructure) |
| **New Relic** | 100GB/mo free | $0.30/GB beyond free tier |
| **Grafana Cloud** | 10K metrics, 50GB logs | Usage-based |

## Decision Tree

```
Do you want open source / no vendor lock-in?
├─ Yes
│  ├─ Do you want managed SaaS?
│  │  ├─ Yes → Grafana Cloud
│  │  └─ No → Self-hosted Prometheus + Grafana
└─ No
   ├─ Do you want all-in-one (metrics + logs + traces)?
   │  ├─ Yes
   │  │  ├─ Do you want APM included?
   │  │  │  ├─ Yes → Datadog or New Relic
   │  │  │  └─ No → Grafana Cloud
   │  └─ No → Prometheus + Loki + Tempo
```

## Migration Guide

### Prometheus to Datadog

```bash
# 1. Install Datadog agent with Prometheus integration
helm install datadog datadog/datadog \
  --set datadog.apiKey=<API_KEY> \
  --set datadog.site=datadoghq.com \
  --set prometheusScrape.enabled=true \
  --set prometheusScrape.serviceEndpoints[0].name=prometheus \
  --set prometheusScrape.serviceEndpoints[0].port=9090

# 2. Verify metrics are flowing
kubectl exec -it <datadog-pod> -- agent status
```

### Prometheus to Grafana Cloud

```bash
# 1. Install Grafana Agent
helm install grafana-agent grafana/grafana-agent \
  --set config.cloudGestureURL=<CLOUD_URL> \
  --set config.apiKey=<API_KEY>

# 2. Configure remote write
kubectl patch configmap grafana-agent -p '{"data":{"agent.yaml": "metrics:\n  configs:\n  - name: prometheus\n    remote_write:\n    - url: <GRAFANA_CLOUD_URL>\n      basic_auth:\n        username: <USER_ID>\n        password: <API_KEY>\n"}}'
```

## Best Practices

| Solution | Practice |
|----------|----------|
| Prometheus | Use Thanos or Cortex for long-term storage |
| Datadog | Use tags for cost allocation |
| New Relic | Use NRQL for custom dashboards |
| Grafana Cloud | Use Loki for log aggregation |

## Related

- [Prometheus](prometheus.md)
- [Grafana](grafana.md)
- [Monitoring Fundamentals](monitoring-fundamentals.md)
- [Alerting](alerting.md)
