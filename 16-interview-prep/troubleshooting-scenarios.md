# Kubernetes Troubleshooting Scenarios

> **Category:** Interview Prep / Troubleshooting
> Real-world troubleshooting scenarios with solutions.

## Scenario 1: Pod Stuck in Pending

### Symptoms
```
NAME                    READY   STATUS    RESTARTS   AGE
my-pod                  0/1     Pending   0          5m
```

### Investigation

```bash
# Check pod events
kubectl describe pod my-pod

# Check node resources
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check resource quotas
kubectl get resourcequotas -n <namespace>
```

### Common Causes

| Cause | Fix |
|-------|-----|
| Insufficient resources | Scale up or optimize |
| Node selector not met | Fix node selector |
| PVC not bound | Check PVC status |
| Taints/tolerations | Add tolerations |

### Solution

```bash
# Option 1: Scale up
kubectl scale deployment <deployment> --replicas=0

# Option 2: Fix node selector
kubectl patch deployment <deployment> -p '{"spec":{"template":{"spec":{"nodeSelector":{"disktype":"ssd"}}}}}'

# Option 3: Add tolerations
kubectl patch deployment <deployment> -p '{"spec":{"template":{"spec":{"tolerations":[{"key":"key","operator":"Equal","value":"value","effect":"NoSchedule"}]}}}}'
```

## Scenario 2: Pod in CrashLoopBackOff

### Symptoms
```
NAME                    READY   STATUS             RESTARTS   AGE
my-pod                  0/1     CrashLoopBackOff   5          10m
```

### Investigation

```bash
# Check logs
kubectl logs my-pod --previous

# Check pod events
kubectl describe pod my-pod

# Check container status
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[*].lastState}'
```

### Common Causes

| Cause | Fix |
|-------|-----|
| Application crash | Fix application |
| Missing config | Add ConfigMap/Secret |
| Wrong command | Fix container command |
| Resource limits | Increase limits |

### Solution

```bash
# Option 1: Check logs
kubectl logs my-pod --previous

# Option 2: Exec into pod
kubectl exec -it my-pod -- sh

# Option 3: Fix config
kubectl create configmap my-config --from-literal=key=value
kubectl patch deployment <deployment> -p '{"spec":{"template":{"spec":{"volumes":[{"name":"config","configMap":{"name":"my-config"}}]}}}}'

# Option 4: Increase resources
kubectl patch deployment <deployment> -p '{"spec":{"template":{"spec":{"containers":[{"name":"my-container","resources":{"limits":{"memory":"256Mi","cpu":"500m"}}}]}}}}'
```

## Scenario 3: Service Not Reachable

### Symptoms
```bash
$ curl http://my-service
curl: (6) Could not resolve host
```

### Investigation

```bash
# Check service
kubectl get svc my-service

# Check endpoints
kubectl get endpoints my-service

# Check selector labels
kubectl get svc my-service -o yaml | grep selector

# Check pod labels
kubectl get pods --show-labels
```

### Common Causes

| Cause | Fix |
|-------|-----|
| No endpoints | Fix selector labels |
| Service not created | Create service |
| DNS not working | Check CoreDNS |
| Network policy | Add allow rules |

### Solution

```bash
# Option 1: Fix selector
kubectl patch svc my-service -p '{"spec":{"selector":{"app":"my-app"}}}'

# Option 2: Create service
kubectl expose deployment my-deployment --port=80 --type=ClusterIP

# Option 3: Check DNS
kubectl run test --image=busybox --rm -it -- nslookup my-service

# Option 4: Fix network policy
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-service
spec:
  podSelector:
    matchLabels:
      app: my-app
  ingress:
  - from: []
    ports:
    - port: 80
EOF
```

## Scenario 4: Node Not Ready

### Symptoms
```
NAME     STATUS     ROLES    AGE   VERSION
node1    NotReady   worker   10d   v1.27.0
```

### Investigation

```bash
# Check node status
kubectl describe node node1

# Check kubelet
ssh node1
sudo systemctl status kubelet

# Check system resources
df -h
free -m
```

### Common Causes

| Cause | Fix |
|-------|-----|
| kubelet not running | Restart kubelet |
| Disk pressure | Free disk space |
| Memory pressure | Free memory |
| Network issues | Check network |

### Solution

```bash
# Option 1: Check kubelet
ssh node1
sudo systemctl restart kubelet

# Option 2: Free disk space
ssh node1
sudo journalctl --vacuum-time=1d
sudo docker system prune -a

# Option 3: Check memory
ssh node1
free -m
sudo reboot

# Option 4: Check network
ssh node1
ping <api-server-ip>
```

## Scenario 5: PVC Stuck in Pending

### Symptoms
```
NAME      STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
my-pvc    Pending                                      gp3            5m
```

### Investigation

```bash
# Check PVC
kubectl describe pvc my-pvc

# Check StorageClass
kubectl get storageclasses

# Check PVs
kubectl get pv
```

### Common Causes

| Cause | Fix |
|-------|-----|
| StorageClass not found | Create StorageClass |
| No available PV | Create PV |
| Provisioner not working | Check provisioner |
| Quota exceeded | Increase quota |

### Solution

```bash
# Option 1: Check StorageClass
kubectl get storageclasses
kubectl describe storageclass gp3

# Option 2: Create StorageClass
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
volumeBindingMode: WaitForFirstConsumer
EOF

# Option 3: Check provisioner
kubectl get pods -n kube-system | grep ebs

# Option 4: Check quotas
kubectl get resourcequotas -n <namespace>
```

## Scenario 6: Deployment Stuck in Rolling Update

### Symptoms
```
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
my-app  1/2     1            1           10m
```

### Investigation

```bash
# Check deployment
kubectl describe deployment my-app

# Check replicaset
kubectl get rs

# Check pods
kubectl get pods -l app=my-app
```

### Common Causes

| Cause | Fix |
|-------|-----|
| New pod not starting | Check pod events |
| Old pod not terminating | Check PDB |
| Image pull error | Fix image |
| Resource limits | Increase limits |

### Solution

```bash
# Option 1: Check pod events
kubectl describe pod <new-pod>

# Option 2: Check PDB
kubectl get pdb
kubectl delete pdb <pdb-name>

# Option 3: Fix image
kubectl set image deployment/my-app my-container=new-image:latest

# Option 4: Rollback
kubectl rollout undo deployment/my-app
```

## Scenario 7: DNS Resolution Failing

### Symptoms
```bash
$ kubectl run test --image=busybox --rm -it -- nslookup kubernetes.default
** server can't find kubernetes.default: NXDOMAIN
```

### Investigation

```bash
# Check CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns

# Check CoreDNS config
kubectl get configmap coredns -n kube-system -o yaml
```

### Common Causes

| Cause | Fix |
|-------|-----|
| CoreDNS not running | Restart CoreDNS |
| ConfigMap missing | Recreate ConfigMap |
| Network policy | Add allow rules |
| Resource limits | Increase limits |

### Solution

```bash
# Option 1: Restart CoreDNS
kubectl rollout restart deployment coredns -n kube-system

# Option 2: Check ConfigMap
kubectl get configmap coredns -n kube-system -o yaml

# Option 3: Check network policy
kubectl get networkpolicies -n kube-system

# Option 4: Increase resources
kubectl patch deployment coredns -n kube-system -p '{"spec":{"template":{"spec":{"containers":[{"name":"coredns","resources":{"limits":{"memory":"256Mi","cpu":"500m"}}}]}}}}'
```

## Scenario 8: Ingress Not Working

### Symptoms
```bash
$ curl http://my-app.example.com
404 Not Found
```

### Investigation

```bash
# Check ingress
kubectl get ingress my-ingress

# Check ingress class
kubectl get ingressclasses

# Check ingress controller
kubectl get pods -n ingress-nginx
```

### Common Causes

| Cause | Fix |
|-------|-----|
| Ingress class not set | Set ingressClassName |
| Controller not running | Start controller |
| Service not found | Create service |
| TLS not configured | Add TLS |

### Solution

```bash
# Option 1: Set ingress class
kubectl patch ingress my-ingress -p '{"spec":{"ingressClassName":"nginx"}}'

# Option 2: Check controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Option 3: Check service
kubectl get svc -n ingress-nginx

# Option 4: Add TLS
kubectl patch ingress my-ingress -p '{"spec":{"tls":[{"hosts":["my-app.example.com"],"secretName":"tls-secret"}]}}'
```

## Scenario 9: OOMKilled Pods

### Symptoms
```
NAME                    READY   STATUS      RESTARTS   AGE
my-pod                  0/1     OOMKilled   5          10m
```

### Investigation

```bash
# Check pod
kubectl describe pod my-pod

# Check resource limits
kubectl get pod my-pod -o jsonpath='{.spec.containers[*].resources}'

# Check memory usage
kubectl top pods
```

### Common Causes

| Cause | Fix |
|-------|-----|
| Memory limit too low | Increase limit |
| Memory leak | Fix application |
| No limits set | Set limits |

### Solution

```bash
# Option 1: Check current limits
kubectl get pod my-pod -o jsonpath='{.spec.containers[*].resources}'

# Option 2: Increase limits
kubectl patch deployment <deployment> -p '{"spec":{"template":{"spec":{"containers":[{"name":"my-container","resources":{"limits":{"memory":"512Mi"}}}]}}}}'

# Option 3: Set requests
kubectl patch deployment <deployment> -p '{"spec":{"template":{"spec":{"containers":[{"name":"my-container","resources":{"requests":{"memory":"256Mi"},"limits":{"memory":"512Mi"}}}]}}}}'

# Option 4: Monitor usage
kubectl top pods -l app=my-app
```

## Scenario 10: ImagePullBackOff

### Symptoms
```
NAME                    READY   STATUS             RESTARTS   AGE
my-pod                  0/1     ImagePullBackOff   0          5m
```

### Investigation

```bash
# Check pod
kubectl describe pod my-pod

# Check image
kubectl get pod my-pod -o jsonpath='{.spec.containers[*].image}'

# Check pull secret
kubectl get pod my-pod -o jsonpath='{.spec.imagePullSecrets}'
```

### Common Causes

| Cause | Fix |
|-------|-----|
| Image not found | Check image name |
| Registry auth | Add pull secret |
| Network issues | Check network |
| Tag doesn't exist | Use correct tag |

### Solution

```bash
# Option 1: Check image
kubectl describe pod my-pod | grep -A 5 "Events"

# Option 2: Create pull secret
kubectl create secret docker-registry regcred \
  --docker-server=<your-registry-server> \
  --docker-username=<your-name> \
  --docker-password=<your-password> \
  --docker-email=<your-email>

# Option 3: Add to deployment
kubectl patch deployment <deployment> -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"regcred"}]}}}}'

# Option 4: Use public image
kubectl set image deployment/my-app my-container=nginx:latest
```

## Related

- [Troubleshooting Patterns](../14-troubleshooting/troubleshooting-patterns.md)
- [Incident Case Studies](../14-troubleshooting/incidents/)
- [Debugging Commands](debugging-commands.md)
- [Interview Questions](interview-questions.md)
