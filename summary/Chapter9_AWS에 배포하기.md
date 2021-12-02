# Chapter 9, AWS에 배포하기

Created: November 9, 2021

# AWS

AWS(Amazon Web Service)는 아마존에서 제공하는 클라우드 서비스다. 

클라우드 서비스란 시스템 배포 및 우녕을 하기 위해 필요한 서버, 데이터베이스, 네트워크 등의 물리적 장치설치를 걱정하지 않고, 클라우드 서비스 제공자의 사이트 혹은 인터페이스를 통해서 쉅게 설정 및 사용할 수 있다.

본 챕터에서는 다음의 서비스들을 사용하여 미니터 API를 배포할 것이다.

- EC2(Elastic Compute Cloud)
- RDS(Relational Database Service)
- ALB(Application Load Balancer)

## RDS

AWS에서 제공하는 데이터베이스 서비스다.  RDS를 사용하면 개발자가 직접 데이터베이스 서버를 설치하고 운용할 필요 없이 데이터베이스를 설정하고 사용할 수 있다. 

## EC2

EC2는 AWS에서 사용하는 서버다. 그러므로 EC2 인스턴스(각각의 서버)에 미니터 서버 API를 배포하면 된다. 필요한 사항과 다양한 운영체제를 제공한다.

## Local Balancer

local balancer는 백엔드 서버들에게 전송되는 HTTP나 다른 종류의 네트워크 트래픽을 여러 서버들에 동일하게 분배해 주는 역할을 한다. local balancer가 HTTP요청을 먼저 받고 그 후 2개의 EC2  인스턴스들에게 균등해 분배해 준다. 그러므로 하나의 서버가 모든 트래픽을 감당하지 않아도 되며, 또한 만일 하나의 서버에 문제가 있어도 복구되는 동안 다른 서버가 트래픽을 감당 해 줄 수 있다.