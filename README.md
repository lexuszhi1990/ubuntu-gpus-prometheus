## gpus stats monitoring via prometheus

### build docker images
docker build -t registry.cn-shenzhen.aliyuncs.com/deeplearn/gpu-stats-exporter:0.4.5 .


### run docker image

docker run --rm -it -v /etc:/host/etc -v /apps/workspace/ubuntu-gpus-prometheus:/app registry.cn-shenzhen.aliyuncs.com/deeplearn/gpu-stats-exporter:0.4.4

