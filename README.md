# WE CAN DO!
### 🌍 프로젝트명 : 11:57PM
- 👨‍👩‍👧‍👦 팀원 : 오도윤, 고병욱(Data) : 데이터 크롤링, 데이터 전처리(명언, 음악, AI 훈련용 데이터셋)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;윤이현, 정범준(AI) : Bert를 활용한 영어, 한글 감정 분석 모델 생성<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;오형동, 강희연(Back-end) : 웹 및 DB 구축, 배포<br>

- 프로젝트 기획 의도 : 우울증을 앓는 인구는 매해 증가하고, 이러한 우울증 치료에 긍정적 영향을 미치는 일기쓰기를 통해<br>
자신의 감정을 파악하고 위로 해줄 수 있는 서비스를 제공하는 것이 목표
![우울증](https://github.com/DY0903/wecando/assets/141305320/986dd210-d2d6-4f15-9b9d-eec53626f66e)
- 하루의 일기를 작성하고 일기에 대한 감정을 분석하여 해당 감정에 따른 명언과 음악을 추천해주는 서비스를 제공합니다.<br><br>

### 📌 Period : 2023.10.30 ~ 2023. 11.29<br><br>

### 😀 감정 분류
|Ekman | 문장에 내재한 감정 분석을 위한 감정 분류 방법<br>（국내 특허)|딥러닝 모델(BERT)과 감정어휘 사전을 <br>결합한 음원가사 감정 분석|
|------|---|---|
|심리학자로 감정연구의 대가|감정사전을 제작하여 감정을 긍정, 부정에서 나아가<br> SVM을 활용디테일하게 분류|가사분석을 딥러닝 모델을 활용하여<br>감정 분석|
|기쁨, 사랑, 놀람, 괴로움, 두려움, 경멸, 분노 : 7가지로 분류|기쁨, 슬픔, 분노, 공포, 중립 : 5가지로 분류|사랑, 즐거움, 열정, 행복, 슬픔, 분노, 외로움, 그리움, 두려움 : 9가지로 분류|

**→ 이를 토대로 프로젝트에서는 감정 라벨링을 기쁨, 사랑(긍정), 슬픔, 분노, 걱정(부정), 중립 6가지로 분류**
<br><br>
### 🎯 대표 기능
- 일기쓰기를 통한 감정분석 후 그에 따른 명언 및 음악 추천
  - 감정분석의 경우 모델을 활용 
- 일기의 경우 개인적인 영역이므로 회원가입 서비스
  - 회원가입에 따른 SNS 계정 연동(Google, Kakao)
  - 회원가입 후 비밀번호 찾기 기능(ID, E-mail 일치 시 비밀번호 재설정 링크 이메일로 전송)
- 일기 표지 꾸미기 기능
  - Konva Java Script 오픈소스 라이브러리를 활용하여 스티커 영역 설정 및 꾸미기 기능(Drag & Drop & Resize)
  - HTML2Canvas Java Script 오픈소스 라이브러리를 활용하여 이미지를 다운로드 할 수 있는 URL 생성
    <br><br>

### 🏗️ 서버 및 DB의 구조

- 서버 : 도커를 활용한 MYSQL
  - 내부 접속만 가능하단 단점, 외부 도메인 활용하여 배포 예정
- 명언 및 음악추천을 위한 DataBase 구조<br>
![wecando - writen](https://github.com/DY0903/wecando/assets/141305320/378fa927-5c88-492d-94ed-ed4e06d44d4c)
<br><br>

### 🎈 모델

- 영어 모델(사전학습 모델인 BERT bert-base-uncased 사용)
  - 활용한 데이터 수 : 56,000여 문장 
  - 불용어 처리없이 모델 훈련을 진행(불용어 처리 전후가 의미가 없었기 때문)
  - 토큰화와 패딩을 통해 문장의 길이 일치
  - 최적화 Optimizer로 Adam W 활용
    - 모델의 과적합을 예방하는데 효과적임
- 한글 모델(사전학습 모델인 BERT bert-multilingual-case 활용)
  - 활용한 데이터 수 : 91,000여 문장
  - 한국어의 경우 은, 는, 이, 가 같은 조사와 보조사가 있기 때문에 불용어 사전을 만들어 불용어 처리 후 훈련 진행
  - 토큰화와 패딩을 통해 문장의 길이 일치
- BERT를 활용한 이유
  - 모델링 중 BERT와 GPT 모델을 활용해 보았으나, 문장의 이해에 있어서 양방향으로 이해하는 BERT 모델이 감정분류에 더 적합하다고 판단
    - GPT의 경우 감성 분류(이진 분류) 혹은 대화 생성형 모델에 좀 더 적합한 것으로 여겨짐
- 모델링을 위한 다양한 시도
  - KoBert : 현재 웹에 로드한 모델에 비해 성능이 높지 않아 활용 불가
  - LSTM : 사전학습 모델인 Bert에 비해 본 프로젝트에서 사용한 평가지표인 accuracy_score 점수가 상대적으로 낮았음
  - SVM : 형태소 분석을 활용하여 감정 분석을 시도 하였으나, 성능이 그다지 높지 않았음
<br><br>
### 🐒 문제점
1. 모델을 불러와 웹에서 감정 평가를 진행함에 있어 로딩이 오래 소요되는 단점 존재
   - apps.py에서 모델의 최초 로딩을 진행 후, view에서 불러오는 형식을 취하여 문제 해결
    #### apps.py
          # 한국어 모델 구성에 필요한 BERT 토크나이저와 모델 로드
          tokenizer_ko = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
          bert_model = TFBertModel.from_pretrained('bert-base-multilingual-cased')
          MAX_LEN = 50
          
          # 영어 모델 PyTorch 모델 로드
          model_path = 'E:/00. KOREA IT/WECANDO/final/wecando/static/wecando/model/영어_최종_Bert.pth'
          model_eng = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=6)
          # 영어 모델을 CPU에서 불러오기
          model_eng.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
          model_eng.eval()
    
          # 한국어 모델 사용자 정의 모델 정의
          class CustomBERTModel(tf.keras.Model):
              def __init__(self, num_classes):
                  super().__init__()
                  self.bert = bert_model
                  # 추가적인 레이어는 필요에 따라 정의
                  self.dropout = tf.keras.layers.Dropout(0.1)  # 예시로 dropout 레이어 추가
                  self.classifier = tf.keras.layers.Dense(num_classes, activation='softmax')
      
              def call(self, inputs, attention_mask=None, token_type_ids=None, training=False):
                  # BERT 모델의 출력을 가져옵니다.
                  outputs = self.bert(inputs, attention_mask=attention_mask, token_type_ids=token_type_ids)
                  pooled_output = outputs.pooler_output
                  pooled_output = self.dropout(pooled_output, training=training)
                  return self.classifier(pooled_output)
      
          # 한국어 모델 선언
          model_ko = CustomBERTModel(6)  # 클래스 개수
      
          # 선언된 한국어 모델에 적절한 입력 데이터 제공하여 내부 구조 초기화
          test_input = tokenizer_ko.encode_plus("테스트 문장", return_tensors='tf', padding='max_length',
                       max_length=128, truncation=True)
          model_ko(test_input['input_ids'], attention_mask=test_input['attention_mask'],
                token_type_ids=test_input['token_type_ids'])
      
          # 한국어 모델 가중치 로드
          model_ko.load_weights('E:/00. KOREA IT/WECANDO/final/wecando/static/wecando/model/1120_saved_model_10epoch.h5')
    
          # 한국어 모델 예측 함수
          def lyrics_evaluation_predict(sentence):
              data_x = WecandoConfig.sentence_convert_data(sentence)  # 문장을 모델 입력 형식으로 변환
              predict = WecandoConfig.model_ko.predict(data_x)
              predict_value = np.ravel(predict[0])
              predict_emotion: {0: '기쁨', 1: '사랑', 2: '슬픔', 3: '분노', 4: '걱정', 5: '중립'}
              # 예측된 클래스의 인덱스를 찾기.
              predicted_class = np.argmax(predict_value)
              return predicted_class
      
          # 영어 모델 예측 함수
          def predict_emotion(text):
      
              text1 = text.replace('[^A-Za-z0-9가-힣 ]', '')
              text2 = text1.lower()
      
              inputs = tokenizer_eng(text2, return_tensors="pt",add_special_tokens=True, padding=True,
                       truncation=True, max_length=512)
              emotion_labels = [0,1,2,3,4,5]
              with torch.no_grad():
                  outputs = model_eng(**inputs)
              prediction = torch.argmax(outputs.logits, dim=1).item()
              return emotion_labels[prediction]
  - 로딩된 모델을 views.py에서 불러와, 문자열에 한글과 영어의 갯수를 센 후 한글과 영어 모델 중 어떤 모델을 활용하여 평가할 것인지 판단
    #### views.py    
          def form_valid(self, form):
            # 일기내용중에 한글과 영어 중 더 많이 사용된 언어의 모델을 사용하기 위해 각 문자의 사용량을 확인
            content = self.request.POST.get("writen_content")
            ko = 0
            eng = 0
            for i in content:
                if (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
                    eng = eng + 1
                else:
                    ko = ko + 1
    
            print(ko, eng)
    
            # 한국어가 더 많으면 한국어 모델을 사용
            if ko >= eng:
    
                a = WecandoConfig.lyrics_evaluation_predict(self.request.POST.get("writen_content"))
                print("한국어 모델 사용 " + str(a))
            
            # 영어가 더 많으면 영어 모델을 사용
            else:
                a = WecandoConfig.predict_emotion(self.request.POST.get("writen_content"))
                print("영어 모델 사용 " + str(a))


2. 모델의 정확도 문제<BR>
   - 프로젝트의 모델과 감정의 종류를 6종으로 분류하고 있는 연구와 정확도를 비교하였을 때, 상당히 높은 수준의 정확도를 보이고 있음에도 불구하고, 모델이 감정을 다르게 분석하는 경우도 있었음
   - 해당 문제를 해결하기 위해 1차적으로 글을 쓰고, 감정의 분류를 사용자가 직접 확인하게 하여 감정의 종류를 다시 한번 체크하여 명확히 분류할 수 있게끔 유도
     <br><br>
    ![감정분류 체크](https://github.com/DY0903/wecando/assets/141305320/7bf1a65a-4e81-4ca4-9b61-5319599a2849)

      
