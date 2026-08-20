# etcd vs Consul vs ZooKeeper

> **Category:** Distributed Systems / Comparisons
> Decision guide for distributed key-value stores.

## Overview

| Feature | etcd | Consul | ZooKeeper |
|---------|------|--------|-----------|
| **Language** | Go | Go | Java |
| **Protocol** | Raft | Raft | ZAB |
| **Data model** | Key-value | Key-value + Service Mesh | Hierarchical |
| **Watch** | Yes | Yes | Yes |
| **Transactions** | Yes | Yes | Yes |
| **Service discovery** | No | Yes | No |
| **Health checks** | No | Yes | No |
| **GUI** | etcdctl | Consul UI | ZooKeeper Inspector |
| **Complexity** | Low | Medium | High |

## When to Use What

### Use etcd When:

- You need **Kubernetes backend**
- You want **simplicity** and **performance**
- You need **strong consistency**
- You want **small footprint**

```bash
# Example: etcd operations
etcdctl put key value
etcdctl get key
etcdctl watch key
etcdctl del key
```

### Use Consul When:

- You need **service discovery**
- You need **service mesh**
- You need **health checks**
- You want **multi-datacenter** support

```bash
# Example: Consul operations
consul kv put key value
consul kv get key
consul kv watch key
consul kv delete key
```

### Use ZooKeeper When:

- You need **distributed coordination**
- You have **existing Hadoop/Kafka** ecosystem
- You need **sequential consistency**
- You want **battle-tested** system

```bash
# Example: ZooKeeper operations
zkCli.sh set /key value
zkCli.sh get /key
zkCli.sh watch /key
zkCli.sh delete /key
```

## Comparison Matrix

| Criteria | etcd | Consul | ZooKeeper |
|----------|------|--------|-----------|
| **Performance** | Very High | High | Medium |
| **Scalability** | High | Very High | Medium |
| **Consistency** | Strong | Strong | Sequential |
| **Availability** | High | Very High | Medium |
| **Ease of use** | Easy | Medium | Hard |
| **Community** | Large | Large | Large |
| **K8s integration** | Native | Plugin | No |

## Decision Tree

```
Do you need Kubernetes backend?
├─ Yes → etcd
└─ No
   ├─ Do you need service discovery/mesh?
   │  ├─ Yes → Consul
   │  └─ No
   │     ├─ Do you have Hadoop/Kafka?
   │     │  ├─ Yes → ZooKeeper
   │     │  └─ No → etcd (default)
```

## Migration Guide

### etcd to Consul

```bash
# Export etcd data
etcdctl get / --prefix --keys-only > keys.txt

# Import to Consul
while read key; do
  value=$(etcdctl get "$key" --print-value-only)
  consul kv put "$key" "$value"
done < keys.txt
```

### Consul to etcd

```bash
# Export Consul data
consul kv export > consul-data.json

# Import to etcd
cat consul-data.json | jq -r 'to_entries[] | "\(.key) \(.value)"' | while read key value; do
  etcdctl put "$key" "$value"
done
```

## Best Practices

| Store | Practice |
|-------|----------|
| etcd | Regular backups, compact history |
| Consul | Use ACLs, enable encryption |
| ZooKeeper | Monitor latency, tune session timeout |

## Related

- [etcd](../02-architecture/etcd.md)
- [Consul](../12-service-mesh/consul.md)
- [ZooKeeper](../12-service-mesh/zookeeper.md)
