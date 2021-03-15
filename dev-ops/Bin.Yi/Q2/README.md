# 说明

这里用Docker镜像作为发布格式，用Kubernetes集群作为宿主和编排系统（运行在GCP GKE中），[Gitlab CI](https://docs.gitlab.com/ee/ci/)作为CI/CD平台。

## 关于自动化CI/CD（实现自动测试，合并门槛，自动部署，指定版本部署）

以下假定[应用程序](https://github.com/goxr3plus/Simplest-Spring-Boot-Hello-World)的源码保存在`./app/`目录中。

在[.gitlab-ci.yml](./.gitlab-ci.yml)文件中实现以下自动化管线：

1. `unit-test`，运行maven的单元测试。此管线在任何commit的时候触发，可以在项目中限制如果unit-test失败则不允许merge到master branch。
2. `build`，运行maven build，生成`.war`文件并保存到artifacts以用于以后的管线。
3. `package`，运行docker build，根据[脚本](./Dockerfile)生成docker image，有两种模式，当任何改变merge到master时，生成以`:PIPELINE_ID`为标签的镜像，作为nightly build。当新增git tag时，生成以`:TAG`为标签的镜像。
4. `integration-test`，在制作好的镜像上进行集成测试，确保镜像可以正常部署。如2/3/4任意步骤失败则不会部署到Kubernetes环境。
5. `deploy`，将镜像部署到Kubernetes（GCP GKE）。这里有两种模式，a. 当生成git tag时，自动部署最新Tag到Kubernetes； b. 当手动运行管线并给出`DEPLOY_TAG`环境变量时，部署指定的Tag到Kubernetes。

__说明__：GKE的API Key file和Gitlab的Registry Password保存在Gitlab工程的环境变量中防止密码泄露。

## 关于Kubernetes编排（实现自动伸缩）

1. app镜像作为deployment部署到环境中，初始副本（Replica）为1，即产生一个Pod。
2. HorizontalPodAutoscaler负责自动横向伸缩，最小数目为1，最大数目为5，伸缩目标为Pod CPU负载不大于80%（单个Pod的CPU用量由Resources/Requests/CPU定义，例子中为100m，即1/10个核心）。
3. 应用程序的Endpoint通过Service暴露给外界，并进行负载均衡，round robin分配到所有Pod上。
4. 当前服务仅在Kubernetes内部暴露，可用port forward进行测试，实际应用中应该通过Ingress和LoadBalancer暴露给外网，并在GCP中设置相应的VPC和防火墙策略。同时能需要设置DNS解析以绑定到指定的域名。

## 关于日志

使用EFK（Elastic Search + FluentD + Kibana)做日志的集成管理，[logging目录](./k8s/logging)给出了基本的manifest以部署到Kubernetes。这几个组件可以实现日志的自动收集（从容器的Stdout或指定文件），元数据增强（标注每一条日志的来源Pod，Node，Deployment等信息），汇总（到Elastic Search），可视化筛选查询（从Kibana）等。

## 关于监控和警报

使用Prometheus平台进行Metrics的收集和索引，同时使用Grafana实现可视化，使用Alert Manager做自动事件管理和警报。Prometheus和其它组件（比如kube-state-metrics，node-exporter，grafana， alert manager）均可以通过helm chart或operator部署到Kubernetes上。

__说明__：日志监控和警报也有许多SAAS的实现，比如NewRelic，Datadog等，提供更好的用户体验和技术支持，同时节省了本身运行和维护Elastic Search等组件的精力/花费，也是不错的选择。
