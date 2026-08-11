# CKA / CKAD / CKS Exam Walkthrough — Domain by Command

> **Category:** Interview Prep / Exams

The certified exams are **hands-on labs** (3h, no multiple choice). Success comes from two things: (1) **speed on `kubectl`** (aliases, imperatives, namespace context), and (2) **knowing which command fixes each objective domain**. This is the scenario→command map for every K8s certification objective — no prose, just the recipe you type at the terminal.

## ⚡ Exam strategy & shortcuts

```bash
export k=kubectl; export do='--dry-run=client -o yaml'
export nowrite="--validate=false"   # when server can't validate yet
k config set-context --current --namespace=team-a   # never retype -n
# copy an object between namespaces (do NOT `kubectl run` + edit):
k get deploy web -n prod -o yaml | sed 's/^    namespace: prod/    namespace: staging/' | k apply -f -
# change image fast (no YAML edit):
k set image deploy/web web=nginx:1.25
# quick manifest then tweak:
k create deployment web --image=nginx $do > web.yaml; $EDITOR web.yaml; k apply -f web.yaml
# force-delete stuck terminating pod:
k get pod <p> -o jsonpath={.metadata.finalizers}   # then:
k patch pod <p> -p '{"metadata":{"finalizers":[]}}' --type=merge
```
- **30 mins in, if stuck, skip and flag** — come back; the cluster can always be fixed later.
- **Every objective has a weight** — attempt ≥1 cheap command even if partial.

## CKA — 6 domains

### 1. Cluster Architecture, Installation & Configuration (15–20%)
```bash
# kubeadm init (single CP); add --control-plane --certificate-key for HA:
sudo kubeadm init --apiserver-advertise-address=$(hostname -i) --pod-network-cidr=192.168.0.0/16 --control-plane-endpoint=$(hostname -i)
# worker join:
sudo kubeadm join <vip>:6443 --token <t> --discovery-token-ca-cert-hash sha256:<hash>
# inspect static-pod manifests:
ls /etc/kubernetes/manifests   # apiserver/controller-manager/scheduler/etcd
# upgrade:
sudo kubeadm upgrade apply v1.31; k drain <node> --ignore-daemonsets; sudo apt install kubelet=1.31...; sudo systemctl restart kubelet; k uncordon <node>
```
> See full reference: [`../08-cluster-operations/kubeadm.md`](../08-cluster-operations/kubeadm.md)

### 2. Core Workloads & Scheduling (30–35%)
```bash
k expose deploy web --port=80 --target-port=8080 --name web-svc           # Service
k run box --image=busybox --restart=Never -- sleep 3600 -- sh -c '...'    # one-off Pod
k create deployment web --image=nginx; k set image deploy/web web=nginx:1.25
k scale deploy web --replicas=5; k rollout status deploy/web; k rollout undo deploy/web
# CronJob:
k create cronjob hello --image=busybox --schedule="*/1 * * * *" -- echo hi
# anti-affinity / taints:
k patch deploy web -p='{"spec":{"template":{"spec":{...}}}}'
```

### 3. Services & Networking (20–25%)
```bash
k get endpoints web-svc; k describe svc web-svc            # debug "no endpoints" = selector mismatch
k port-forward svc/web-svc 8080:80
# NetworkPolicy: default deny, then allow app tier:
cat <<EOF | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: web-np }
spec:
  podSelector: { matchLabels: {app: web} }
  policyTypes: [Ingress,Egress]
  ingress: [{from:[{podSelector:{matchLabels:{app: api}}}]}]
  egress: []
EOF
```

### 4. Storage (10–15%)
```bash
k get sc; k describe sc
# expand a PVC:
k patch sc <name> -p '{"allowVolumeExpansion":true}'; k patch pvc <pvc> -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
# snapshot restore:
apiVersion: snapshot.storage.k8s.io/v1; kind: VolumeSnapshot ...
```

### 5. Troubleshooting (10–15%)
```bash
k get events -A --sort-by=.lastTimestamp
k describe pod <p>; k logs -p <p>              # -p = previous container
k exec -it <p> -- /bin/sh; k exec -it <p> -c c2 -- /bin/sh
k top nodes; k top pods -n ...                 # needs metrics-server
k cordon <n>; k drain <n> --ignore-daemonsets; k uncordon <n>
```

## CKAD — 5 domains (imperative-first)

### Configuration: ConfigMaps & Secrets
```bash
k create configmap cfg --from-literal=KEY=val --from-file=app.properties
k create secret generic db --from-literal=user=admin --from-literal=pass=pwd -o yaml $do
# mount as env + volume:
volumeMounts: [{name:c,name:cfg,configMap:{name:cfg}}]   # envFrom / valueFrom / volumes[].configMap
```

### Multi-container Pods (sidecar / init)
```bash
k run web --image=nginx --restart=Never --restart=Never  # then edit; share emptyDir:
# init container pattern:
initContainers: [{name:init,image:busybox,command:["sh","-c","until..."]}]
```

### Probes, Service Mesh & Ingress
```bash
# liveness/readiness tuning:
readinessProbe: {httpGet:{path:/,port:8080},initialDelaySeconds:2,periodSeconds:3}
# Ingress:
k create ingress web --class=nginx --rule="host.com/=web-svc:80" --tls=tls-secret
```

### Helm / Package Mgmt
```bash
helm install web ./chart -f values-prod.yaml --set image.tag=v2
helm test web; helm rollback web 1   # fix a bad rollout
```

## CKS — 5 domains (hardening + supply chain)

### 1. Cluster Hardening (25%)
```bash
# CIS: only allow authorized network CIDRs; RBAC; --authorization-mode=RBCA? no:
APISERVER: --authorization-mode=Webhook,Node     # NodeRestriction must be on
# disable anonymous + service-account tokens:
kube-apiserver: --anonymous-auth=false
kubelet: --read-only-port=0 --rotate-certificates=true --anonymous-auth=false
# short-lived SA tokens:
apiVersion: v1, kind: ServiceAccount, metadata:..., secrets: []   # no bound token; or tokenRequest with expirationSeconds
# seccomp:
securityContext: {seccompProfile:{type:RuntimeDefault}}
```

### 2. Network (10%)
```bash
# Default-deny + allow control-plane egress only; CoreDNS only via kubelet (ClusterDNS)
k get endpoints kube-dns -n kube-system          # should be reachable only by pods with the label
```

### 3. Registry & Image Security (25%)
```bash
cosign sign ghcr.io/org/app:tag                 # keyless OIDC
cosign verify ghcr.io/org/app:tag --certificate-oidc-issuer=https://token.actions.githubusercontent.com
# admission: Kyverno/OPA policy "only signed images"
```

### 4. Logging & Monitoring (15%)
```bash
# AlertManager route + severity; kube-state-metrics; node-exporter; audit-log:
kube-apiserver: --audit-policy-file=... --audit-log-path=...
```

### 5. Supply Chain / Runtime (15%)
```bash
# SBOM + image scan in CI (Trivy/Grype); runtime class for untrusted workloads:
kind: RuntimeClass; handler: kata   # gVisor/wasm for multi-tenant
```

## ⏱ Time-box cheat sheet
| Task | 90s command |
|------|-------------|
| Make a Pod use a Secret as env | `k create secret...; envFrom/...` |
| Debug no endpoints | `k get endpoints <svc>; k describe svc` |
| Roll back | `k rollout undo deploy/<x>` |
| Drain+safe reboot | `k drain <n> --ignore-daemonsets --delete-local-data; k uncordon <n>` |
| Resize PVC | `k patch sc ...allowVolumeExpansion; k patch pvc <x> -p '{...storage:...}'` |

## Interview Questions

**Q: You have 30 min left with 8 objectives unsolved. What do you do?**
A: Skip nothing *unattempted* — for each remaining objective, write the minimum valid manifest (even `kubectl create` + `k apply` of a placeholder), then flag it and return. Partial credit exists; empty answers score zero.

**Q: How do you copy a Deployment from `prod` to `staging` in one line?**
A: `kubectl get deploy web -n prod -o yaml | sed 's/^    namespace: prod/    namespace: staging/' | kubectl apply -f -`

**Q: What three `kube-apiserver` flags harden the control plane most on the CKS?**
A: `--authorization-mode=Webhook,Node` (with NodeRestriction on), `--anonymous-auth=false`, plus kubelet flags `--authorization-mode=Webhook --read-only-port=0 --rotate-certificates=true`.

## Related Resources
- [CKA](cka.md) · [CKAD](ckad.md) · [CKS](cks.md) · [Study Plan](study-plan.md) · [Exam Checklist](exam-checklist.md)
- [kubectl Debug](../14-troubleshooting/kubectl-debug.md) · [Exam cheatsheet](../cheat-sheets/cert-cheatsheet.md)
- Full reference: [kubeadm](../08-cluster-operations/kubeadm.md), [Security](../06-security/security.md), [Troubleshooting Encyclopedia](../14-troubleshooting/troubleshooting-encyclopedia.md)
