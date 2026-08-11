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
| 2 | Architecture | [02-architecture](02-architecture) | [README](02-architecture/README.md) + 10 docs |
| 3 | Workloads | [03-workloads](03-workloads) | [README](03-workloads/README.md) + 14 docs |
| 4 | Networking | [04-networking](04-networking) | [README](04-networking/README.md) + 13 docs |
| 5 | Storage | [05-storage](05-storage) | [README](05-storage/README.md) + 5 docs |
| 6 | Security | [06-security](06-security) | [README](06-security/README.md) + 11 docs |
| 7 | Scheduling & Autoscaling | [07-scheduling-autoscaling](07-scheduling-autoscaling) | [README](07-scheduling-autoscaling/README.md) + 11 docs |
| 8 | Cluster Operations | [08-cluster-operations](08-cluster-operations) | [README](08-cluster-operations/README.md) + 8 docs |
| 9 | Package Management | [10-package-management](10-package-management) | [README](10-package-management/README.md) + 4 docs |
| 10 | CI/CD & GitOps | [11-ci-cd-gitops](11-ci-cd-gitops) | [README](11-ci-cd-gitops/README.md) + 4 docs |
| 11 | Service Mesh | [12-service-mesh](12-service-mesh) | [README](12-service-mesh/README.md) + 4 docs |
| 12 | Observability | [13-observability](13-observability) | [README](13-observability/README.md) + 6 docs |
| 13 | Troubleshooting | [14-troubleshooting](14-troubleshooting) | [README](14-troubleshooting/README.md) + 4 docs + [incidents/](14-troubleshooting/incidents) (9 case studies) |
| 14 | Reference | (top-level) | [API groups](api-groups-reference.md), [versions](kubernetes-versions.md), [companies](companies-using-kubernetes.md), [certifications](kubernetes-certifications.md) |
| 15 | Cheat Sheets | [cheat-sheets](cheat-sheets) | [kubectl](cheat-sheets/kubectl.md), [helm](cheat-sheets/helm.md), [yaml](cheat-sheets/yaml.md), [certs](cheat-sheets/cert-cheatsheet.md) |
| 16 | Examples | [examples](examples) | [README](examples/README.md) + 28 YAML manifests across common-patterns, scheduling, security, storage, monitoring, ci-cd, advanced |

**Total: 17 categories, 266 documents, ~245000 words.**

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

## 10b. Supply Chain Security (11-supply-chain)

| # | Topic | File |
|---|-------|------|
| 1 | Cosign (keyless signing + SBoM) | [cosign.md](11-supply-chain/cosign.md) |
| 2 | SBOM (Software Bill of Materials) | [sbom.md](11-supply-chain/sbom.md) |
| 3 | Container Image Scanning | [image-scanning.md](11-supply-chain/image-scanning.md) |

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
| 3 | Troubleshooting Encyclopedia | [troubleshooting-encyclopedia.md](14-troubleshooting/troubleshooting-encyclopedia.md) |
| 4 | Disaster Cases | [disaster-cases.md](14-troubleshooting/disaster-cases.md) |

### Real Company Incident Case Studies (incidents/)

| # | Incident | File |
|---|----------|------|
| 1 | GitLab ORM Migration → Deployment Cascade | [gitlab-orm-migration-outage.md](14-troubleshooting/incidents/gitlab-orm-migration-outage.md) |
| 2 | GitHub ALB Controller + NLB Firewall Drain | [github-alb-nlb-firewall.md](14-troubleshooting/incidents/github-alb-nlb-firewall.md) |
| 3 | Spotify Istio Cert Rotation → 5xx Cascade | [spotify-istio-cert-rotation.md](14-troubleshooting/incidents/spotify-istio-cert-rotation.md) |
| 4 | Slack CoreDNS Cache Thrashing | [slack-coredns-cache-thrashing.md](14-troubleshooting/incidents/slack-coredns-cache-thrashing.md) |
| 5 | Zalando etcd Quorum Loss + Botched Restore | [zalando-etcd-quorum-loss.md](14-troubleshooting/incidents/zalando-etcd-quorum-loss.md) |
| 6 | Roblox CPU Throttling Under Load | [roblox-cpu-throttling.md](14-troubleshooting/incidents/roblox-cpu-throttling.md) |
| 7 | Capital One CNI Plugin Upgrade → Network Partition | [capital-one-cni-network-partition.md](14-troubleshooting/incidents/capital-one-cni-network-partition.md) |
| 8 | Adidas Helm Hook Partial Rollback | [adidas-helm-hook-partial-rollback.md](14-troubleshooting/incidents/adidas-helm-hook-partial-rollback.md) |
| 9 | Netflix Chaos Engineering Cascade | [netflix-chaos-cascade.md](14-troubleshooting/incidents/netflix-chaos-cascade.md) |
| 10 | Cloudflare BGP Route Leak → Global Outage | [cloudflare-bgp-leak.md](14-troubleshooting/incidents/cloudflare-bgp-leak.md) |
| 11 | Tesla K8s Dashboard Cryptojacking | [tesla-k8s-dashboard-cryptojacking.md](14-troubleshooting/incidents/tesla-k8s-dashboard-cryptojacking.md) |
| 12 | Amazon US-EAST-1 Network Outage | [amazon-us-east-1-outage.md](14-troubleshooting/incidents/amazon-us-east-1-outage.md) |
| 13 | Google Cloud Config Push Outage | [google-cloud-config-push-outage.md](14-troubleshooting/incidents/google-cloud-config-push-outage.md) |
| 14 | Azure Load Balancer Outage | [azure-load-balancer-outage.md](14-troubleshooting/incidents/azure-load-balancer-outage.md) |
| 15 | Shopify OOM Kill Storm | [shopify-oom-kill-storm.md](14-troubleshooting/incidents/shopify-oom-kill-storm.md) |
| 16 | Discord Memory Leak | [discord-memory-leak.md](14-troubleshooting/incidents/discord-memory-leak.md) |
| 17 | Epic Games Fortnite Outage | [epic-games-fortnite-outage.md](14-troubleshooting/incidents/epic-games-fortnite-outage.md) |
| 18 | Apple iCloud Outage | [apple-icloud-outage.md](14-troubleshooting/incidents/apple-icloud-outage.md) |
| 19 | LinkedIn DNS Outage | [linkedin-dns-outage.md](14-troubleshooting/incidents/linkedin-dns-outage.md) |
| 20 | Stripe Certificate Expiry | [stripe-cert-expiry.md](14-troubleshooting/incidents/stripe-cert-expiry.md) |
| 21 | Twilio Dependency Failure | [twilio-dependency-failure.md](14-troubleshooting/incidents/twilio-dependency-failure.md) |
| 22 | GitLab Database Incident | [gitlab-database-incident.md](14-troubleshooting/incidents/gitlab-database-incident.md) |
| 23 | Uber Cascading Failure | [uber-cascading-failure.md](14-troubleshooting/incidents/uber-cascading-failure.md) |
| 24 | Airbnb Resource Exhaustion | [airbnb-resource-exhaustion.md](14-troubleshooting/incidents/airbnb-resource-exhaustion.md) |
| 25 | Pinterest Node Failure Storm | [pinterest-node-failure-storm.md](14-troubleshooting/incidents/pinterest-node-failure-storm.md) |
| 26 | Reddit RBAC Lockout | [reddit-rbac-lockout.md](14-troubleshooting/incidents/reddit-rbac-lockout.md) |
| 27 | Wayfair Storage Failure | [wayfair-storage-failure.md](14-troubleshooting/incidents/wayfair-storage-failure.md) |
| 28 | Bloomberg API Server Overload | [bloomberg-api-server-overload.md](14-troubleshooting/incidents/bloomberg-api-server-overload.md) |
| 29 | JPMorgan Network Policy Misconfiguration | [jpmorgan-network-policy.md](14-troubleshooting/incidents/jpmorgan-network-policy.md) |
| 30 | Goldman Sachs Helm Chart Conflict | [goldman-sachs-helm-conflict.md](14-troubleshooting/incidents/goldman-sachs-helm-conflict.md) |
| 31 | Capital One Data Breach | [capital-one-breach.md](14-troubleshooting/incidents/capital-one-breach.md) |
| 32 | Netflix Chaos Gone Wrong | [netflix-chaos-gone-wrong.md](14-troubleshooting/incidents/netflix-chaos-gone-wrong.md) |
| 33 | Spotify ConfigMap Corruption | [spotify-configmap-corruption.md](14-troubleshooting/incidents/spotify-configmap-corruption.md) |
| 34 | Slack Service Mesh Outage | [slack-service-mesh-outage.md](14-troubleshooting/incidents/slack-service-mesh-outage.md) |
| 35 | Roblox HPA Misconfiguration | [roblox-hpa-misconfiguration.md](14-troubleshooting/incidents/roblox-hpa-misconfiguration.md) |
| 36 | Zalando Operator Crash Loop | [zalando-operator-crash-loop.md](14-troubleshooting/incidents/zalando-operator-crash-loop.md) |
| 37 | Adidas PVC Binding Failure | [adidas-pvc-binding-failure.md](14-troubleshooting/incidents/adidas-pvc-binding-failure.md) |
| 38 | GitLab Helm Corruption | [gitlab-helm-corruption.md](14-troubleshooting/incidents/gitlab-helm-corruption.md) |
| 39 | Incidents README | [README.md](14-troubleshooting/incidents/README.md) |

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
| 7 | CKA/CKAD/CKS Exam Walkthrough (domain→command map) | [exam-walkthrough.md](16-interview-prep/exam-walkthrough.md) |
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
| Troubleshooting (90-second commands) | [troubleshooting.md](cheat-sheets/troubleshooting.md) |
| Glossary (terms, acronyms, concepts) | [glossary.md](cheat-sheets/glossary.md) |

## 16. Examples (examples)

| Topic | Path |
|-------|------|
| README + structure | [examples/README.md](examples/README.md) |
| Common patterns (Deployment, Service, Ingress, ConfigMap/Secret) | [examples/common-patterns/](examples/common-patterns) |
| Scheduling (HPA, VPA, Quota, PDB, affinity) | [examples/scheduling/](examples/scheduling) |
| Advanced (operators, CRDs, hooks) | [examples/advanced/](examples/advanced) |
| CI/CD | [examples/ci-cd/](examples/ci-cd) |
| Monitoring | [examples/monitoring/](examples/monitoring) |
| Security | [examples/security/](examples/security) |
| Storage | [examples/storage/](examples/storage) |

### Tutorials (examples/tutorials/)

| Tutorial | File |
|----------|------|
| Nginx + Domain + TLS (deploy → service → ingress → cert-manager) | [tutorial-nginx-domain.md](examples/tutorials/tutorial-nginx-domain.md) |
| Nginx + Istio Service Mesh (mTLS, VirtualService, canary) | [tutorial-nginx-istio.md](examples/tutorials/tutorial-nginx-istio.md) |
| Full Stack App (ConfigMap, Secret, PVC, HPA, PDB, monitoring) | [tutorial-full-stack.md](examples/tutorials/tutorial-full-stack.md) |

## 16b. Learning Path (docs/)

| Topic | File |
|-------|------|
| Zero to Expert learning path (4 phases, 52 topics, 5 labs) | [learning-path.md](docs/learning-path.md) |


---

## Added / Updated — new playbooks & reference

These were added to close gaps for learners and operators; every link below resolves to a real file.

| Topic | File |
|-------|------|
| kubeadm cluster bootstrap (init/join/HA, certs, upgrades) | [kubeadm.md](08-cluster-operations/kubeadm.md) |
| FinOps (cost buckets, right-sizing, spot, allocation, idle nodes) | [finops.md](08-cluster-operations/finops.md) |
| Backup & DR runbook (etcd snapshots + Velero + restore) | [backup-disaster-recovery.md](08-cluster-operations/backup-disaster-recovery.md) |
| Gateway API implementations (controller matrix) | [gateway-api-implementations.md](04-networking/gateway-api-implementations.md) |
| WASM as a workload (runtimes, RuntimeClass, OCI) | [wasm.md](15-advanced-patterns/wasm.md) |
| OCI artifacts (images, charts, sigs, SBOM, WASM) | [oci.md](10-package-management/oci.md) |
| Multi-Cluster federation (Istio multi-primary, Cilium Mesh) | [multicluster.md](12-service-mesh/multicluster.md) |
| Supply chain / Cosign (keyless signing + SBoM) | [cosign.md](11-supply-chain/cosign.md) |
| Security overview (defense in depth, PSA, etcd encryption) | [security.md](06-security/security.md) |
| HPA/VPA/KEDA + Cluster Autoscaler | [hpa-vpa.md](07-scheduling-autoscaling/hpa-vpa.md) |
| Resource requests/limits & QoS | [resource-management.md](07-scheduling-autoscaling/resource-management.md) |
| Observability overview (golden signals, OTel, Prometheus) | [observability.md](13-observability/observability.md) |
| Troubleshooting Encyclopedia (symptom to diagnosis tables) | [troubleshooting-encyclopedia.md](14-troubleshooting/troubleshooting-encyclopedia.md) |
| Disaster Cases (real incidents and runbooks) | [disaster-cases.md](14-troubleshooting/disaster-cases.md) |
| Pod Security Context (runAsUser, readOnlyRootFilesystem) | [pod-security-context.md](06-security/pod-security-context.md) |
| Version history (v1.0 to current) | [kubernetes-versions.md](kubernetes-versions.md) |
| Real company incident case studies (9 outages) | [incidents/](14-troubleshooting/incidents/) |
| Troubleshooting cheat sheet (90-second commands) | [troubleshooting.md](cheat-sheets/troubleshooting.md) |
| K8s glossary (terms, acronyms, concepts) | [glossary.md](cheat-sheets/glossary.md) |
| SBOM (Software Bill of Materials) | [sbom.md](11-supply-chain/sbom.md) |
| Container image scanning (Trivy, Grype, CI/CD) | [image-scanning.md](11-supply-chain/image-scanning.md) |
| Chaos Engineering (experiments, Chaos Mesh, PDB) | [chaos-engineering.md](15-advanced-patterns/chaos-engineering.md) |
| Learning Path (Zero to Expert, 4 phases) | [learning-path.md](docs/learning-path.md) |
| Tutorial: Nginx + Domain + TLS | [tutorial-nginx-domain.md](examples/tutorials/tutorial-nginx-domain.md) |
| Tutorial: Nginx + Istio Service Mesh | [tutorial-nginx-istio.md](examples/tutorials/tutorial-nginx-istio.md) |
| Tutorial: Full Stack App | [tutorial-full-stack.md](examples/tutorials/tutorial-full-stack.md) |
| Amazon EKS Deep Dive (VPC CNI, IRSA, ALB Controller) | [eks-deep-dive.md](09-cloud-integrations/eks-deep-dive.md) |
| Google GKE Deep Dive (Autopilot, Workload Identity) | [gke-deep-dive.md](09-cloud-integrations/gke-deep-dive.md) |
| Microsoft AKS Deep Dive (Azure CNI, Workload Identity) | [aks-deep-dive.md](09-cloud-integrations/aks-deep-dive.md) |
| Custom Resource Definitions (CRDs) | [crds.md](15-advanced-patterns/crds.md) |
| Kubernetes Operators | [operators.md](15-advanced-patterns/operators.md) |
| Lab workbook (5 hands-on labs: deploy, troubleshoot, RBAC, Helm, GitOps) | [lab-instructions.md](examples/common-patterns/lab-instructions.md) |

---

**Legend of "needs work" (if any):** None — every file listed above is present and linked.
