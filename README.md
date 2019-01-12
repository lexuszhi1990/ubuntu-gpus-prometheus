## gpus stats monitoring via prometheus

### build docker images
docker build -t gpu-stats-prometheus:v0.3 .


### run docker image

docker run --rm -it -v /etc:/host/etc -v /apps/workspace/ubuntu-gpus-prometheus:/app registry.cn-shenzhen.aliyuncs.com/deeplearn/gpu-stats-exporter:0.4.4


docker run --rm -it -v /etc:/host/etc -v /home/train/ws/ubuntu-gpus-prometheus:/app registry.k8s.imagedt.local/gpu-stats-exporter:v0.5.2

docker run --rm -it -v /etc:/host/etc registry.k8s.imagedt.local/gpu-stats-exporter:v0.5

