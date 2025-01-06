## 기획
- 기간 2024.07.03 ~ 2024.08.16
![Untitled (4)](https://github.com/user-attachments/assets/7de6774c-7133-4d82-be02-acd07f18d2cd)
- 프로젝트 주제: ai를 이용하여 시그니처 기반 nids+행위탐지 기반 nids 개발
> |                    Name                    |  맡은 부분  |
> | :----------------------------------------: | :---------: |
> | 안대현 | 시그니처 기반 탐지 nids |
> | 양성혁 | 행위 기반 탐지 nids |
> | 이효원 | 도커 인프라 구축, 개발 |
<br></br>
- 시그니처 기반 nids
  - https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/NIDS_AI/signature.md
- 행위탐지 기반 nids
  - https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/NIDS_AI/anomaly.md
- 도커 인프라 구축 개발 문서
  - https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/NIDS_AI/docker_setting.md

## 배경
- 기존 네트워크 침입 탐지 시스템(NIDS)은 시그니처 기반 탐지 방식으로, 미리 정의된 악성 트래픽 패턴 또는 시그니처와 네트워크 트래픽을 비교하여 위험을 탐지하는 방식이다. 이미 알려진 위협에 대해서는 높은 정확도를 제공하며, 악성 트래픽에 대해 탐지가 빠르고 신뢰성이 높다는 장점이 있다. 다만, 제로 데이 공격이나 새로운 공격에 대해서는 시그니처 업데이트가 필요하다는 단점이 존재함. 이러한 단점을 보완하기 위해 행위 기반 탐지 NIDS 장점인 네트워크 트래픽의 비정상적인 행동 패턴을 탐지하여 위협을 식별하는 방식을 추가하기로 했다.

![image](https://github.com/user-attachments/assets/c3a123aa-a4c2-44ab-82e6-573b0e91fb67)

## 기획 내용

### NIDS 구성도
![image](https://github.com/user-attachments/assets/72c68458-fceb-4508-ae0a-33ad54841718)
-우리의 NIDS는 Out of band 구조로, NIDS가 주시하는 도메인 서버의 부하를 최대한 줄이고자 했다. 이 과정에서 최근 떠오르는 프로세스 격리 기반 컨테이너 가상화 플랫폼인 docker를 활용하여 웹 서버 구축 및 NIDS 모델 서버를 구축하는 네트워크 인프라를 구성했다

### 개발 단계
![image](https://github.com/user-attachments/assets/cd3380a2-04b3-41a8-94a9-5b1aeb19eb17)

### 형상 관리
![image](https://github.com/user-attachments/assets/345e6eb0-0255-45ea-a3e0-c1ca1852147e)
-코드 형상 관리의 경우 깃허브를 활용했고, 개발 문서는 노션에 정리, 일반적인 소통의 경우 디스코드 채널을 활용했다.

*깃허브 레포 주소:* https://github.com/Laiika06/WeNeeds

*노션 개발 문서 주소: [구름톤 트레이닝 Final Project [WeNeeds]](https://www.notion.so/Final-Project-WeNeeds-92322320a9df480487f00360d6a0958d?pvs=21)*


### 역할 분담
![image](https://github.com/user-attachments/assets/61d1d130-ff43-4e46-bebf-83e1091a86a9)
-역할 분담의 경우, 행위 기반 탐지 NIDS 개발, 시그니처 기반 탐지 NIDS 개발, 이외 네트워크 인프라 구성 및 테스트용 웹 서버 구축으로 나누었다.

### 개발 방법
![image](https://github.com/user-attachments/assets/bf0d1cb8-7b26-43ed-9a2f-874851025751)
**행위 기반 탐지 NIDS 개발**의 경우, NSL-KDD 데이터셋을 활용해 머신러닝을 진행하고 악성 사용자의 행위를 탐지할 수 있도록 했다.

**시그니처 기반 탐지 NIDS 개발**의 경우, 스노트룰을 직접 파싱하여 시그니처 DB를 구축하고 해당 성능을 검증할 수 있도록 했다.

**연구용 웹 서버 개발 및 도커 인프라 구축**의 경우, 도커를 활용해 네트워크를 구축하고 해당 NIDS를 정상적으로 웹 서버에 탑재할 수 있도록 준비했다.

## 개발 과정

### 도커 인프라 및 웹 서버 구축
- nids 테스트를 위해 여러 기능이 있는 웹 서버 구축, 해킹을 시도하여 NIDS 테스트
- 사용한 기술 스택
  - mysql, php, python, docker, bash
- 도커 컨테이너 구성
![image](https://github.com/user-attachments/assets/fcf2aad6-6b83-4bc1-af93-95a8cd926ac3)
- 컨테이너를 docker compose를 활용하여 편리하게 실행할 수 있게 구성함

## 행위기반 탐지 NIDS
- docker, phython, shell, html 사용
- NSL-KDD 데이터 셋 활용하여 머신 러닝 진행
- 시간 상 모든 공격 유형을 구분하지는 못하고 공격일 시 1, 공격이 아닐 시 0을 반환하게 모델링 함

![image](https://github.com/user-attachments/assets/a5c4277d-ecda-468d-9688-3621ecc42b8b)
- 여러 알고리즘 중 해당 알고리즘의 성능이 높게 나와 random forest 알고리즘을 선택
![image](https://github.com/user-attachments/assets/196c66dd-7853-45dc-9514-e6cd24b85c9b)
- 해당 알고리즘은 여러 개의 decision tree 알고리즘을 결합한 방식으로 decision tree 여러 개의 결과를 보고, 최종적으로 다수결로 판단하여 결론을 내리는 방식으로 작동한다.

![image](https://github.com/user-attachments/assets/3e42f8c2-8450-41e4-880f-c50076e069b2)
-랜덤 포레스트 모델의 변수 중요도 평가 기능을 활용하여 NSL-KDD 데이터셋의 변수 축소를 시도. 42개 변수 중 중요도 상위 변수들을 1개부터 20개까지 늘려가며 성능을 테스트한 결과, 상위 4개 변수만으로도 높은 성능을 달성하여 효율적인 학습이 가능함을 확인했다. 이를 통해 프로젝트 기간 내에 효과적인 모델 개발을 이루었다

![image](https://github.com/user-attachments/assets/00235782-99d5-40d9-8e07-a845a1befaa0)
- 사용한 변수: src_bytes, dst_bytes, same_srv_rate, dst_host_srv_count

![image](https://github.com/user-attachments/assets/0a212208-01fc-4700-9c7f-c92693fddff3)
- 학습시킨 모델을 .pkl 파일로 추출하여 패키징 후 사용

![image](https://github.com/user-attachments/assets/cebc237e-1dc3-46c2-8d42-05caac9e7699)
- 위 사진은 웹 서버 컨테이너에서 tcp dump를 활용하여 패킷을 캡처하는 모습이다
- docker volumes를 활용하여 pcap 파일로 저장
- 이후 저장한 파일을 nids 컨테이너에서 읽어와 학습에 사용한 4가지 변수를 추출
- 4개의 변수로 NIDS 모델이 예측을 수행

## 시그니처 기반 탐지 NIDS
- python을 사용

![image](https://github.com/user-attachments/assets/1dc4fca5-af4b-4936-87e8-297c4c662e3d)
- 스노트 룰을 활용하여 직접 룰을 파싱하는 작업을 수행했다. 그 과정에서 화살표의 방향을 통일하고, 포트 번호를 표시되게 하는 등의 룰 단순화 작업을 실시했다

![image](https://github.com/user-attachments/assets/6b7d6afd-6363-474d-9f6a-2f5e0cbc6d30)
- 슬라이드에 나타낸 룰셋 이외에도 약 300개 이상의 스노트 룰셋을 파싱했는데, 스노트 전체 룰셋의 10% 수준 밖에 되지 않아 성능 개선이 필요하다고 판단했다. 이는 추후 진행 예정이다

![image](https://github.com/user-attachments/assets/f25bd80c-7401-42cb-8396-5081e7ef80a8)
- 룰셋에서 파싱한 변수들을 활용하여 실제 패킷에서 추출한 변수와 비교하는 방식으로 모델을 구성 하였다

![image](https://github.com/user-attachments/assets/01307987-7bd0-4f66-a5d6-b85f4e2a1a26)
- 테스트의 경우, 피해자 서버는 metasploitable 2를 활용했고, 공격자 서버는 host PC의 칼리 리눅스를 활용했다. Echo Chargen bomb으로 해당 룰셋이 공격을 잘 테스트하는 지 판단했다

![image](https://github.com/user-attachments/assets/9ef87c60-756a-4aa4-a1d7-c80cb762488c)
- 탐지 결과 시그니처 기반 탐지 NIDS가 잘 작동하는 모습을 볼 수 있었다

### 자체 피드백 및 보완점 시사
행위 기반 탐지 NIDS의 경우, 머신 러닝 단계에서 더 많은 변수들을 사용했으면 더 정확한 공격 탐지가 가능했을 것이다. 또한, 공격 유형을 사용자가 확인할 수 있으면 더 정확하고 신속한 대응이 가능하기 때문에 악성 행위가 어떤 공격 유형으로 추측되는지 사용자에게 알려줄 수 있는 기능을 구현한다면 더 완성도 있는 프로젝트가 될 것 같다.

또한, 행위 기반 탐지 NIDS와 시그니처 기반 탐지 NIDS를 통합해 하나의 NIDS를 구축하려 했으나 시간이 부족해 각각 모듈화 시켜 따로 구성했던 점, 기획 단계에서 대시보드는 시각화가 가능하게 구성하려 했지만 이 부분 또한 시간 상의 이유로 로그 형식으로 대체한 점이 아쉬웠던 부분이다.
부족한 부분이 많은 프로젝트였지만, 해당 프로젝트를 꾸준히 디벨롭해 완성도를 높이고자 한다
