# Monitoring Examples

> Prometheus Operator, alerting, and Grafana dashboard-as-code.

## Contents
- `app-service-monitor.yaml` — app exposing /metrics + Service + ServiceMonitor.  OK
- `service-monitor.yaml` — standalone ServiceMonitor for an existing Service.  OK
- `prometheus-alert.yaml` — an SLO-style alert rule.  OK
- `grafana-dashboard.yaml` — a Grafana Dashboard JSON (CPU + memory panels) in a ConfigMap.  OK

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
