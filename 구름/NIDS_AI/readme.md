### 기획
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
  - 

- 개선해야 할 점
  - 프로젝트 시간 부족으로 행위 기반 탐지ndis와 시그니처 기반 탐지 nids를 통합하지 못하였음
  - 행위 기반 탐지 nids를 도커 서버에 적용하고 실험해 본 결과 여러 공격을 탐지하지 못하였음
    - ai 학습과정에서 데이터셋이 잘못된 상태로 학습이 진행되었거나 변수가 적어서 생긴 것으로 추측
  - 시그니처 탐지 nids를 도커 환경에서 실행해 볼 필요가 있음
