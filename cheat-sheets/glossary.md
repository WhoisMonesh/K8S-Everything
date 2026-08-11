# Kubernetes Glossary — Terms, Acronyms & Concepts

> **Category:** Reference / Quick Reference
> Every K8s term you'll see in docs, interviews, and production.

## Core Concepts

| Term | Definition |
|------|-----------|
| **Pod** | Smallest deployable unit; one or more containers sharing network/Storage. |
| **Node** | Physical or virtual machine running kubelet + container runtime. |
| **Cluster** | Set of nodes managed by a control plane (API server, etcd, scheduler, controller-manager). |
| **Control Plane** | The "brain" — API server, etcd, scheduler, controller-manager, cloud-controller-manager. |
| **Data Plane** | Where workloads run — kubelet, container runtime, CNI plugin, kube-proxy. |
| **Namespace** | Virtual cluster within a physical cluster; isolates resources and RBAC. |

## Workloads

| Term | Definition |
|------|-----------|
| **Deployment** | Manages ReplicaSets; declarative updates, rollbacks, scaling. |
| **ReplicaSet** | Maintains a stable set of N identical pods. |
| **StatefulSet** | For stateful workloads; stable network identity, persistent storage, ordered deployment. |
| **DaemonSet** | Ensures one pod runs on every (or selected) node. |
| **Job** | Runs pods to completion (batch). |
| **CronJob** | Schedules Jobs on a cron expression. |
| **Pod Disruption Budget (PDB)** | Limits voluntary disruptions (e.g., node drain) to ensure minimum availability. |
| **Horizontal Pod Autoscaler (HPA)** | Scales pod count based on CPU/memory/custom metrics. |
| **Vertical Pod Autoscaler (VPA)** | Right-sizes pod resource requests/limits. |
| **Cluster Autoscaler** | Adds/removes nodes based on pending pods or utilization. |

## Networking

| Term | Definition |
|------|-----------|
| **Service** | Stable network endpoint (ClusterIP, NodePort, LoadBalancer) mapping to pods. |
| **Ingress** | HTTP/HTTPS routing rules (path-based, host-based) via an Ingress Controller. |
| **Gateway API** | Next-gen Ingress (Kubernetes SIG); supports TCP/UDP, weighted routing, backend policies. |
| **CNI (Container Network interface)** | Plugin standard for pod networking (Calico, Cilium, Flannel, AWS VPC CNI). |
| **CoreDNS** | DNS server for service discovery (`<service>.<namespace>.svc.cluster.local`). |
| **NodelocalDNS** | DNS cache daemonset on each node; reduces CoreDNS load. |
| **Network Policy** | Firewall rules for pod-to-pod traffic (ingress/egress). |
| **Service Mesh** | Layer-7 network (Istio, Linkerd); mTLS, traffic management, observability. |
| **Envoy** | L4/L7 proxy used as sidecar in service meshes. |
| **mTLS** | Mutual TLS; both client and server authenticate via certificates. |
| **Sidecar** | Helper container in a pod (e.g., Envoy proxy, log collector). |

## Storage

| Term | Definition |
|------|-----------|
| **PersistentVolume (PV)** | Cluster-level storage resource (NFS, EBS, GCE PD). |
| **PersistentVolumeClaim (PVC)** | Request for storage by a pod; binds to a PV. |
| **StorageClass** | Defines provisioner, parameters, and reclaim policy for dynamic PV creation. |
| **Dynamic Provisioning** | Automatic PV creation when a PVC is submitted (no manual PV needed). |
| **Reclaim Policy** | `Retain` (keep PV), `Delete` (delete with PVC), `Recycle` (deprecated). |
| **Volume Snapshot** | Point-in-time copy of a PVC for backup/restore. |

## Security

| Term | Definition |
|------|-----------|
| **RBAC** | Role-Based Access Control; Role, ClusterRole, RoleBinding, ClusterRoleBinding. |
| **ServiceAccount (SA)** | Identity for pods; pods assume SA to access API/cloud resources. |
| **IRSA** | IAM Roles for Service Accounts (AWS); SA → IAM role mapping. |
| **Workload Identity** | GCP/Azure equivalent of IRSA; SA → cloud IAM binding. |
| **Pod Security Standards (PSS)** | `privileged`, `baseline`, `restricted` — enforce security profiles. |
| **Pod Security Admission (PSA)** | Enforces PSS via labels on namespaces (`enforce`, `audit`, `warn`). |
| **SecurityContext** | Per-pod or per-container security settings (runAsUser, capabilities, readOnlyRootFilesystem). |
| **Seccomp** | Secure computing mode; restricts syscalls a container can make. |
| **AppArmor** | Mandatory access control; limits file/network/capability access. |
| **Network Policy** | Firewall rules for pod-to-pod traffic. |

## Cluster Operations

| Term | Definition |
|------|-----------|
| **etcd** | Distributed key-value store; the cluster's source of truth. |
| **kubelet** | Node agent; manages pods, reports status, runs health checks. |
| **kube-proxy** | Maintains iptables/IPVS rules for Service load balancing. |
| **kubeadm** | Tool for bootstrapping a Kubernetes cluster. |
| **Certificate Authority (CA)** | Signs kubelet/apiserver/client certs; root of trust. |
| **Kubeconfig** | File containing cluster, user, and context info (`~/.kube/config`). |
| **Context** | Named cluster+user+namespace combination in kubeconfig. |
| **kubectl** | CLI for interacting with the Kubernetes API. |
| **Helm** | Package manager for Kubernetes (charts, releases, values). |
| **Chart** | Helm package; templates + values + metadata. |
| **Release** | A deployed instance of a Helm chart. |

## Scheduling & Placement

| Term | Definition |
|------|-----------|
| **Scheduler** | Assigns pods to nodes based on constraints (resources, affinity, taints). |
| **Taint** | Node-level repulsion; pods without a matching toleration are not scheduled. |
| **Toleration** | Pod-level acceptance of a node's taint. |
| **Node Affinity** | Pod preference/requirement for specific nodes (by label). |
| **Pod Affinity/Anti-Affinity** | Co-locate or separate pods based on labels. |
| **Topology Spread Constraints** | Distribute pods across zones/nodes evenly. |
| **PriorityClass** | Preemption priority; higher-priority pods can evict lower-priority ones. |
| **Resource Quota** | Limits total CPU/memory/PVC count per namespace. |
| **LimitRange** | Default/min/max resource limits per pod/container in a namespace. |

## Observability

| Term | Definition |
|------|-----------|
| **Metrics** | Quantitative data (CPU, memory, request rate). Prometheus, Datadog. |
| **Logs** | Event streams from pods/nodes. Loki, ELK, Fluentd. |
| **Traces** | Distributed request paths across services. Jaeger, Tempo, OpenTelemetry. |
| **Golden Signals** | Latency, Traffic, Errors, Saturation (SRE framework). |
| **SLI/SLO/SLA** | Service Level Indicator/Objective/Agreement — reliability targets. |
| **Error Budget** | Allowed failure rate (1 - SLO); consumed by incidents. |
| **Prometheus** | Metrics collection + alerting (pull-based, PromQL). |
| **Grafana** | Dashboards for Prometheus/Loki/tempo data. |
| **AlertManager** | Routes Prometheus alerts (email, Slack, PagerDuty). |

## Supply Chain & CI/CD

| Term | Definition |
|------|-----------|
| **GitOps** | Declarative infrastructure via Git as single source of truth. |
| **ArgoCD** | GitOps controller; syncs K8s manifests from Git repos. |
| **Flux** | GitOps toolkit; reconciles cluster state with Git. |
| **Cosign** | Container image signing (Sigstore); keyless or key-based. |
| **SBOM** | Software Bill of Materials; lists all dependencies in an image. |
| **Syft** | SBOM generator (SPDX/CycloneDX format). |
| **Trivy** | Vulnerability scanner for containers, filesystems, Git repos. |
| **Notary** | Content trust for Docker images (signature verification). |
| **In-Toto** | Supply chain integrity framework; verifies build provenance. |

## Acronyms

| Acronym | Full Form |
|---------|-----------|
| **CNI** | Container Network Interface |
| **CSI** | Container Storage Interface |
| **CRD** | Custom Resource Definition |
| **CRB** | ClusterRoleBinding |
| **PDB** | Pod Disruption Budget |
| **HPA** | Horizontal Pod Autoscaler |
| **VPA** | Vertical Pod Autoscaler |
| **SA** | ServiceAccount |
| **RBAC** | Role-Based Access Control |
| **PSA** | Pod Security Admission |
| **PSS** | Pod Security Standards |
| **IRSA** | IAM Roles for Service Accounts |
| **SDS** | Secret Discovery Service (Istio) |
| **mTLS** | Mutual Transport Layer Security |
| **L4/L7** | Layer 4 (TCP)/Layer 7 (HTTP) |
| **QoS** | Quality of Service (Guaranteed/Burstable/BestEffort) |
| **OOMKilled** | Out of Memory Killed |
| **CrashLoopBackOff** | Pod repeatedly crashing and restarting |
| **ImagePullBackOff** | Kubelet can't pull container image |
| **ErrImagePull** | Image pull failed (transient) |
| **Evicted** | Pod evicted due to node pressure (disk/memory/PID) |
| **Preempted** | Lower-priority pod evicted for higher-priority pod |
| **Finalizer** | Cleanup hook; prevents resource deletion until hook completes |
| **OwnerReference** | Links child resource to parent (e.g., ReplicaSet → Deployment) |
| **Annotation** | Arbitrary key-value metadata (not used for selection) |
| **Label** | Key-value metadata for selection (services, selectors, policies) |
| **Selector** | Filter resources by labels (e.g., `app=nginx`) |

## Related

- [Kubernetes Architecture](../02-architecture/README.md)
- [Core Concepts](../01-core-concepts/README.md)
- [Cheat Sheets](../cheat-sheets/)
