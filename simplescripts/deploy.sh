set -x
set -e

echo "Запуск minikube..."
minikube start

echo "Установка Istio"
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.20.0 sh -
export PATH="$PWD/istio-1.20.0/bin:$PATH"
istioctl install --set profile=demo -y
kubectl apply -f istio-1.20.0/samples/addons/prometheus.yaml
kubectl label namespace default istio-injection=enabled --overwrite

echo "Сборка Docker-образа..."
eval $(minikube -p minikube docker-env)
docker build -t flask-app-image .

echo "Применение ConfigMap & Service & Deployment для Flask-приложения..."
kubectl apply -f config/flask-app.yaml

echo "Применение DaemonSet..."
kubectl apply -f config/daemonset.yaml

echo "Применение CronJob..."
kubectl apply -f config/cronjob.yaml

sleep 10

echo "Применение настроек Istio-компонентов"
kubectl apply -f config/istio-destinationrule.yaml
kubectl apply -f config/istio-gateway.yaml
kubectl apply -f config/istio-virtualservice.yaml

sleep 10

# UPDATE:

echo "Установка Prometheus"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f ./config/prometheus-values.yaml

sleep 10

echo "Применение ServiceMonitor для приложения"
kubectl apply -f config/prometheus-monitor.yaml

echo "Развертывание завершено."
sleep 10
kubectl wait --for=condition=ready pod -l app=flask-app --timeout=120s
kubectl get all