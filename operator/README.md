# Overview

Short guide about how to deploy and test the static routes operator.

## Prerequisites

1. A working DOKS cluster you have access to.
2. Kubectl CLI installed on your local machine, and configured to point to your DOKS cluster.
3. A git client to clone the [k8s-staticroute-operator](https://github.com/digitalocean/k8s-staticroute-operator/) repo.
4. NAT GW Droplet configured and running as detailed [here](https://docs.digitalocean.com/products/networking/vpc/how-to/configure-droplet-as-gateway/).

**Note**:

**Make sure your NAT GW Droplet is created in the same VPC as your DOKS cluster.**

## Deploying the Static Routes Operator

1. Clone this repo:

    ```shell
    git clone https://github.com/digitalocean/k8s-staticroute-operator.git
    ```

2. Change directory to local copy:

    ```shell
    cd k8s-staticroute-operator/
    ```

3. Deploy the static routes operator to your DOKS cluster:

    ```shell
    kubectl apply -k operator/
    ```

4. Check if operator Pods are up and running:

    ```shell
    kubectl get pods -l name=static-route-operator -n static-routes
    ```

    Output looks similar to:

    ```text
    NAME                          READY   STATUS    RESTARTS   AGE
    static-route-operator-9vp7g   1/1     Running   0          22m
    static-route-operator-mlfff   1/1     Running   0          22m
    ```

5. Check operator logs - no exceptions should be reported:

    ```shell
    kubectl logs -f ds/static-route-operator -n static-routes
    ```

    Output looks similar to:

    ```text
    [2022-08-24 14:42:13,625] kopf._core.reactor.r [DEBUG   ] Starting Kopf 1.35.6.
    [2022-08-24 14:42:13,625] kopf._core.engines.a [INFO    ] Initial authentication has been initiated.
    [2022-08-24 14:42:13,626] kopf.activities.auth [DEBUG   ] Activity 'login_via_pykube' is invoked.
    [2022-08-24 14:42:13,628] kopf.activities.auth [DEBUG   ] Pykube is configured in cluster with service account.
    [2022-08-24 14:42:13,629] kopf.activities.auth [INFO    ] Activity 'login_via_pykube' succeeded.
    [2022-08-24 14:42:13,629] kopf.activities.auth [DEBUG   ] Activity 'login_via_client' is invoked.
    [2022-08-24 14:42:13,631] kopf.activities.auth [DEBUG   ] Client is configured in cluster with service account.
    [2022-08-24 14:42:13,632] kopf.activities.auth [INFO    ] Activity 'login_via_client' succeeded.
    [2022-08-24 14:42:13,632] kopf._core.engines.a [INFO    ] Initial authentication has finished.
    [2022-08-24 14:42:13,789] kopf._cogs.clients.w [DEBUG   ] Starting the watch-stream for customresourcedefinitions.v1.apiextensions.k8s.io cluster-wide.
    [2022-08-24 14:42:13,791] kopf._cogs.clients.w [DEBUG   ] Starting the watch-stream for staticroutes.v1.kopf.dev cluster-wide.
    ...
    ```

## Testing the Sample Static Routes

Each sample CRD provided creates a static route to two different websites which report back your public IP - [ifconfig.me/ip](http://ifconfig.me/ip), and [ipinfo.io/ip](http://ipinfo.io/ip).

Before applying the CRDs, make sure to change the gateway field to point to your NAT GW Droplet private IP:

```yaml
apiVersion: kopf.dev/v1
kind: StaticRoute
metadata:
  name: static-route-ifconfig.me
spec:
  destination: "34.160.111.145"
  gateway: "<YOUR_NAT_GW_DROPLET_PRIVATE_IP_HERE>"
```

Now, apply a sample manifest from within the `k8s-staticroute-operator` directory to test the setup (make sure to replace the `<>` placeholders first inside the manifest file):

```shell
# Example for ifconfig.me
kubectl apply -f operator/testing/static-route-ifconfig.me.yaml

# Example for ipinfo.io
kubectl apply -f operator/testing/static-route-ipinfo.io.yaml
```

Next, check if the static route resources were created:

```shell
kubectl get staticroutes
```

The output looks similar to:

```text
NAME                       DESTINATION      GATEWAY      AGE
static-route-ifconfig.me   34.160.111.145   10.116.0.5   7m2s
static-route-ipinfo.io     34.117.59.81     10.116.0.5   4s
```

Now, check if the custom static routes were applied on each worker node, after SSH-ing:

```shell
route -n
```

The output looks similar to (the irrelevant lines were omitted from the output for better visibility):

```text
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         206.81.0.1      0.0.0.0         UG    0      0        0 eth0
...
34.117.59.81    10.116.0.5      255.255.255.255 UGH   0      0        0 eth1
34.160.111.145  10.116.0.5      255.255.255.255 UGH   0      0        0 eth1
...
```

**Note:**

In the above example the NAT GW private IP used for testing is `10.116.0.5`.

Next, deploy the `curl-test` Pod to test the setup (make sure you change directory to `k8s-staticroute-operator` first):

```shell
kubectl apply -f operator/testing/curl-test.yaml
```

Finally, test if the curl-test pod replies back your NAT GW public IP for each route:

```shell
# Test ifconfig.me/ip endpoint
kubectl exec -it curl-test -- curl ifconfig.me/ip
```

```shell
# Test the ipinfo.io/ip endpoint
kubectl exec -it curl-test -- curl ipinfo.io/ip
```

## Cleaning Up

To clean up the operator and associated resources, please run the following command from within the `k8s-staticroute-operator` directory:

```shell
kubectl delete -k operator/
```

The output looks similar to:

```text
customresourcedefinition.apiextensions.k8s.io "staticroutes.kopf.dev" deleted
serviceaccount "static-route-operator" deleted
clusterrole.rbac.authorization.k8s.io "static-route-operator" deleted
clusterrolebinding.rbac.authorization.k8s.io "static-route-operator" deleted
daemonset.apps "static-route-operator" deleted
```

Check the routes on each worker node, after SSH-ing:

```shell
route -n
```

The custom static routes should not be present in the routing table output.

Finally, the `curl-test` pod should report back the public IP of the worker node where it runs:

```shell
# Inspect the node where the curl-test Pod runs:
kubectl get pod curl-test -o wide
```

The output looks similar to (write down the node name from the `NODE` column):

```shell
NAME        READY   STATUS    RESTARTS      AGE    IP             NODE            NOMINATED NODE   READINESS GATES
curl-test   1/1     Running   2 (45m ago)   165m   10.244.0.140   basicnp-7micg   <none>           <none>
```

Above example reports - `basicnp-7micg`.

Check the worker node public IP:

```shell
kubectl get nodes -o wide
```

The output looks similar to (note the public IP of the associated node where the `curl-test` Pod runs):

```text
NAME            STATUS   ROLES    AGE     VERSION   INTERNAL-IP   EXTERNAL-IP      OS-IMAGE                       KERNEL-VERSION          CONTAINER-RUNTIME
basicnp-7micg   Ready    <none>   3h20m   v1.23.9   10.116.0.2    206.189.231.90   Debian GNU/Linux 10 (buster)   5.10.0-0.bpo.15-amd64   containerd://1.4.13
basicnp-7micw   Ready    <none>   3h20m   v1.23.9   10.116.0.3    206.81.2.154     Debian GNU/Linux 10 (buster)   5.10.0-0.bpo.15-amd64   containerd://1.4.13
```

Above example reports - `206.189.231.9`.

Exec the `ifconfig.me/ip` curl:

```shell
kubectl exec -it curl-test -- curl ifconfig.me/ip
```

The output looks similar to:

```text
206.189.231.9
```
