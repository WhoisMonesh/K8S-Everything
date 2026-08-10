# Complete Kubernetes Components Index

> The exhaustive list of all Kubernetes concepts, components, tools, and patterns in this repository. **Every link points to a real, documented file.**

## Legend

| Legend | Meaning |
|--------|---------|
| ✅ | Documented — detailed architecture, YAML examples, commands, best practices, interview Q&A |

---

## Category Map

| # | Category | Directory | Documents |
|---|----------|-----------|-----------|
| 1 | Core Concepts | [01-core-concepts](01-core-concepts) | [README](01-core-concepts/README.md) + 16 docs |
| 2 | Architecture | [02-architecture](02-architecture) | [README](02-architecture/README.md) + 9 docs |
| 3 | Workloads | [03-workloads](03-workloads) | [README](03-workloads/README.md) + 14 docs |
| 4 | Networking | [04-networking](04-networking) | [README](04-networking/README.md) + 9 docs |
| 5 | Storage | [05-storage](05-storage) | [README](05-storage/README.md) + 5 docs |
| 6 | Security | [06-security](06-security) | [README](06-security/README.md) + 9 docs |
| 7 | Scheduling & Autoscaling | [07-scheduling-autoscaling](07-scheduling-autoscaling) | [README](07-scheduling-autoscaling/README.md) + 9 docs |
| 8 | Cluster Operations | [08-cluster-operations](08-cluster-operations) | [README](08-cluster-operations/README.md) + 4 docs |
| 9 | Package Management | [10-package-management](10-package-management) | [README](10-package-management/README.md) + 3 docs |
| 10 | CI/CD & GitOps | [11-ci-cd-gitops](11-ci-cd-gitops) | [README](11-ci-cd-gitops/README.md) + 4 docs |
| 11 | Service Mesh | [12-service-mesh](12-service-mesh) | [README](12-service-mesh/README.md) + 3 docs |
| 12 | Observability | [13-observability](13-observability) | [README](13-observability/README.md) + 4 docs |
| 13 | Troubleshooting | [14-troubleshooting](14-troubleshooting) | [README](14-troubleshooting/README.md) + 2 docs |
| 14 | Reference | (top-level) | [API groups](api-groups-reference.md), [versions](kubernetes-versions.md), [companies](companies-using-kubernetes.md), [certifications](kubernetes-certifications.md) |
| 15 | Cheat Sheets | [cheat-sheets](cheat-sheets) | [kubectl](cheat-sheets/kubectl.md), [helm](cheat-sheets/helm.md), [yaml](cheat-sheets/yaml.md), [certs](cheat-sheets/cert-cheatsheet.md) |
| 16 | Examples | [examples](examples) | [README](examples/README.md) + per-topic YAML patterns |

**Total: ~15 core categories, ~115 documents, ~125k words.**

---

## 1. Core Concepts (01-core-concepts)

| # | Concept | File |
|---|---------|------|
| 1 | Kubernetes | [kubernetes.md](01-core-concepts/kubernetes.md) |
| 2 | Pod | [pods.md](01-core-concepts/pods.md) |
| 3 | Pod Lifecycle | [pod-lifecycle.md](01-core-concepts/pod-lifecycle.md) |
| 4 | ReplicaSet | [replicasets.md](01-core-concepts/replicasets.md) |
| 5 | Deployment | [deployments.md](01-core-concepts/deployments.md) |
| 6 | Namespace | [namespaces.md](01-core-concepts/namespaces.md) |
| 7 | Service | [services.md](01-core-concepts/services.md) |
| 8 | Label & Selector | [labels-selectors.md](01-core-concepts/labels-selectors.md) |
| 9 | Annotation | [annotations.md](01-core-concepts/annotations.md) |
| 10 | ConfigMap | [configmaps.md](01-core-concepts/configmaps.md) |
| 11 | Secret | [secrets.md](01-core-concepts/secrets.md) |
| 12 | Volume | [volumes.md](01-core-concepts/volumes.md) |
| 13 | PersistentVolume & PVC | [persistent-volumes.md](01-core-concepts/persistent-volumes.md) |
| 14 | Resource Quota | [resource-quotas.md](01-core-concepts/resource-quotas.md) |
| 15 | Limit Range | [limit-ranges.md](01-core-concepts/limit-ranges.md) |
| 16 | Pod Disruption Budget | [pod-disruption-budgets.md](01-core-concepts/pod-disruption-budgets.md) |

## 2. Architecture (02-architecture)

| # | Component | File |
|---|-----------|------|
| 1 | Kubernetes Architecture | [architecture.md](02-architecture/architecture.md) |
| 2 | kube-apiserver | [kube-apiserver.md](02-architecture/kube-apiserver.md) |
| 3 | etcd | [etcd.md](02-architecture/etcd.md) |
| 4 | kube-scheduler | [kube-scheduler.md](02-architecture/kube-scheduler.md) |
| 5 | kube-controller-manager | [kube-controller-manager.md](02-architecture/kube-controller-manager.md) |
| 6 | cloud-controller-manager | [cloud-controller-manager.md](02-architecture/cloud-controller-manager.md) |
| 7 | kubelet | [kubelet.md](02-architecture/kubelet.md) |
| 8 | kube-proxy | [kube-proxy.md](02-architecture/kube-proxy.md) |
| 9 | Container Runtimes | [container-runtimes.md](02-architecture/container-runtimes.md) |
| 10 | CNCF Landscape | [cncf-landscape.md](02-architecture/cncf-landscape.md) |

## 3. Workloads (03-workloads)

| # | Component | File |
|---|-----------|------|
| 1 | Pod | [pods.md](03-workloads/pods.md) |
| 2 | ReplicaSet | [replicasets.md](03-workloads/replicasets.md) |
| 3 | Deployment | [deployments.md](03-workloads/deployments.md) |
| 4 | Deployment Strategies | [deployment-strategies.md](03-workloads/deployment-strategies.md) |
| 5 | StatefulSet | [statefulsets.md](03-workloads/statefulsets.md) |
| 6 | DaemonSet | [daemonsets.md](03-workloads/daemonsets.md) |
| 7 | Job | [jobs.md](03-workloads/jobs.md) |
| 8 | CronJob | [cronjobs.md](03-workloads/cronjobs.md) |
| 9 | Horizontal Pod Autoscaler | [hpa.md](03-workloads/hpa.md) |
| 10 | Vertical Pod Autoscaler | [vpa.md](03-workloads/vpa.md) |
| 11 | KEDA | [keda.md](03-workloads/keda.md) |
| 12 | Cluster Autoscaler | [cluster-autoscaler.md](03-workloads/cluster-autoscaler.md) |
| 13 | Priority Classes | [priority-classes.md](03-workloads/priority-classes.md) |
| 14 | Pod Disruption Budget | [pdb.md](03-workloads/pdb.md) |

## 4. Networking (04-networking)

| # | Component | File |
|---|-----------|------|
| 1 | Kubernetes Networking | [networking.md](04-networking/networking.md) |
| 2 | Service | [services.md](04-networking/services.md) |
| 3 | CoreDNS | [coredns.md](04-networking/coredns.md) |
| 4 | Ingress | [ingress.md](04-networking/ingress.md) |
| 5 | Ingress Controllers | [ingress-controllers.md](04-networking/ingress-controllers.md) |
| 6 | NGINX Ingress Controller | [nginx-ingress.md](04-networking/nginx-ingress.md) |
| 7 | Traefik Ingress | [traefik-ingress.md](04-networking/traefik-ingress.md) |
| 8 | Network Policies | [network-policies.md](04-networking/network-policies.md) |
| 9 | CNI & kube-proxy (under the hood) | [cni-kube-proxy.md](04-networking/cni-kube-proxy.md) |
| 10 | CNI Plugins | [cni-plugins.md](04-networking/cni-plugins.md) |

## 5. Storage (05-storage)

| # | Component | File |
|---|-----------|------|
| 1 | Volume Fundamentals | [storage.md](05-storage/storage.md) |
| 2 | PersistentVolume & PVC | [persistent-volumes.md](05-storage/persistent-volumes.md) |
| 3 | StorageClass | [storage-classes.md](05-storage/storage-classes.md) |
| 4 | Inline Volumes | [inline-volumes.md](05-storage/inline-volumes.md) |
| 5 | Volume Snapshots | [volume-snapshots.md](05-storage/volume-snapshots.md) |

## 6. Security (06-security)

| # | Component | File |
|---|-----------|------|
| 1 | RBAC Overview | [rbac.md](06-security/rbac.md) |
| 2 | ServiceAccount | [service-accounts.md](06-security/service-accounts.md) |
| 3 | Secrets | [secrets.md](06-security/secrets.md) |
| 4 | Pod Security Admission | [pod-security-admission.md](06-security/pod-security-admission.md) |
| 5 | PodSecurityPolicy (Legacy) | [podsecuritypolicy.md](06-security/podsecuritypolicy.md) |
| 6 | Admission Controllers | [admission-controllers.md](06-security/admission-controllers.md) |
| 7 | OPA Gatekeeper | [opa-gatekeeper.md](06-security/opa-gatekeeper.md) |
| 8 | Kyverno | [kyverno.md](06-security/kyverno.md) |
| 9 | TLS Certificates | [certificates.md](06-security/certificates.md) |

## 7. Scheduling & Autoscaling (07-scheduling-autoscaling)

| # | Concept | File |
|---|---------|------|
| 1 | Kubernetes Scheduling | [scheduling.md](07-scheduling-autoscaling/scheduling.md) |
| 2 | Taints & Tolerations | [taints-tolerations.md](07-scheduling-autoscaling/taints-tolerations.md) |
| 3 | Node Affinity | [node-affinity.md](07-scheduling-autoscaling/node-affinity.md) |
| 4 | Pod Affinity & Anti-Affinity | [pod-affinity.md](07-scheduling-autoscaling/pod-affinity.md) |
| 5 | Resource Requests & Limits | [resources.md](07-scheduling-autoscaling/resources.md) |
| 6 | Limit Range | [limit-ranges.md](07-scheduling-autoscaling/limit-ranges.md) |
| 7 | Resource Quota | [resource-quotas.md](07-scheduling-autoscaling/resource-quotas.md) |
| 8 | Priority Classes | [priority-classes.md](07-scheduling-autoscaling/priority-classes.md) |
| 9 | Topology Spread | [topology-spread.md](07-scheduling-autoscaling/topology-spread.md) |

## 8. Cluster Operations (08-cluster-operations)

| # | Topic | File |
|---|-------|------|
| 1 | Cluster Operations Overview | [README.md](08-cluster-operations/README.md) |
| 2 | kubelet | [kubelet.md](08-cluster-operations/kubelet.md) |
| 3 | Debugging | [debugging.md](08-cluster-operations/debugging.md) |
| 4 | Backup & Restore (etcd + Velero) | [backup-restore.md](08-cluster-operations/backup-restore.md) |
| 5 | Cluster & Component Upgrades | [upgrades.md](08-cluster-operations/upgrades.md) |

## 9. Package Management (10-package-management)

| # | Tool | File |
|---|------|------|
| 1 | Helm | [helm.md](10-package-management/helm.md) |
| 2 | Helm Charts | [helm-charts.md](10-package-management/helm-charts.md) |
| 3 | Kustomize | [kustomize.md](10-package-management/kustomize.md) |

## 10. CI/CD & GitOps (11-ci-cd-gitops)

| # | Topic | File |
|---|-------|------|
| 1 | CI/CD Overview | [ci-cd.md](11-ci-cd-gitops/ci-cd.md) |
| 2 | Argo CD | [argo-cd.md](11-ci-cd-gitops/argo-cd.md) |
| 3 | Flux | [flux.md](11-ci-cd-gitops/flux.md) |
| 4 | Tekton | [tekton.md](11-ci-cd-gitops/tekton.md) |

## 11. Service Mesh (12-service-mesh)

| # | Topic | File |
|---|-------|------|
| 1 | Service Mesh Overview (mTLS, sidecar injection) | [service-mesh.md](12-service-mesh/service-mesh.md) |
| 2 | Istio (control plane, VirtualService, PeerAuthentication) | [istio.md](12-service-mesh/istio.md) |
| 3 | Linkerd (lightweight mesh, identity, policy) | [linkerd.md](12-service-mesh/linkerd.md) |

## 12. Observability (13-observability)

| # | Topic | File |
|---|-------|------|
| 1 | Monitoring Fundamentals (metrics, logs, traces, RED/USE) | [monitoring-fundamentals.md](13-observability/monitoring-fundamentals.md) |
| 2 | Prometheus (Operator, ServiceMonitor, alerts, PromQL) | [prometheus.md](13-observability/prometheus.md) |
| 3 | Grafana (dashboards, data sources, alerting) | [grafana.md](13-observability/grafana.md) |
| 4 | Logging (Fluent Bit, Loki, Elasticsearch, structured logs) | [logging.md](13-observability/logging.md) |

## 13. Troubleshooting (14-troubleshooting)

| # | Topic | File |
|---|-------|------|
| 1 | Troubleshooting Patterns (Pending, CrashLoopBackOff, ImagePull, Services, DNS) | [troubleshooting-patterns.md](14-troubleshooting/troubleshooting-patterns.md) |
| 2 | kubectl Debug (describe, logs, ephemeral containers, port-forward) | [kubectl-debug.md](14-troubleshooting/kubectl-debug.md) |

---

## 14. Interview Prep (16-interview-prep)

| # | Topic | File |
|---|-------|------|
| 1 | CKA - Certified Kubernetes Administrator | [cka.md](16-interview-prep/cka.md) |
| 2 | CKAD - Certified Kubernetes Application Developer | [ckad.md](16-interview-prep/ckad.md) |
| 3 | CKS - Certified Kubernetes Security Specialist | [cks.md](16-interview-prep/cks.md) |
| 4 | Certification Study Plan | [study-plan.md](16-interview-prep/study-plan.md) |
| 5 | CKA Practice Tests | [cka-practice.md](16-interview-prep/cka-practice.md) |
| 6 | Exam Day Checklist | [exam-checklist.md](16-interview-prep/exam-checklist.md) |
| 7 | Debugging Commands | [debugging-commands.md](16-interview-prep/debugging-commands.md) |
| 8 | Conceptual Interview Questions | (inline Q&A in each certification doc) |

## 15. Reference (top-level)

| Topic | File |
|-------|------|
| K8s API Groups, Resources & Verbs | [api-groups-reference.md](api-groups-reference.md) |
| Version cycles, skew policy, upgrade paths | [kubernetes-versions.md](kubernetes-versions.md) |
| Companies Using Kubernetes | [companies-using-kubernetes.md](companies-using-kubernetes.md) |
| Certifications (CKA, CKAD, CKS) | [kubernetes-certifications.md](kubernetes-certifications.md) |

## 15. Cheat Sheets (cheat-sheets)

| Tool | File |
|------|------|
| kubectl | [kubectl.md](cheat-sheets/kubectl.md) |
| Helm | [helm.md](cheat-sheets/helm.md) |
| YAML | [yaml.md](cheat-sheets/yaml.md) |
| CKA/CKAD/CKS exam | [cert-cheatsheet.md](cheat-sheets/cert-cheatsheet.md) |

## 16. Examples (examples)

| Topic | Path |
|-------|------|
| README + structure | [examples/README.md](examples/README.md) |
| Common patterns (PVC, RBAC, HPA, etc.) | [examples/common-patterns/](examples/common-patterns) |
| Advanced (operators, CRDs, hooks) | [examples/advanced/](examples/advanced) |
| CI/CD | [examples/ci-cd/](examples/ci-cd) |
| Monitoring | [examples/monitoring/](examples/monitoring) |
| Security | [examples/security/](examples/security) |
| Storage | [examples/storage/](examples/storage) |

---

**Legend of "needs work" (if any):** None — every file listed above is present and linked.
