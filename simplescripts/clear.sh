kubectl delete -f config/cronjob.yaml
kubectl delete -f config/daemonset.yaml
kubectl delete -f config/flask-app.yaml
kubectl delete -f config/istio-destinationrule.yaml
kubectl delete -f config/istio-gateway.yaml
kubectl delete -f config/istio-virtualservice.yaml

# UPDATE:

export PATH="$PWD/istio-1.20.0/bin:$PATH"
istioctl uninstall -y --purge || echo "istioctl не найден или Istio уже удалён"
minikube stop