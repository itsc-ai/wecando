from django.apps import AppConfig
import tensorflow as tf
import numpy as np
from transformers import TFBertModel, BertTokenizer, DistilBertTokenizer, DistilBertForSequenceClassification, BertForSequenceClassification
import torch
import nltk

# BERT 토크나이저와 모델 로드
tokenizer_ko = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
bert_model = TFBertModel.from_pretrained('bert-base-multilingual-cased')
MAX_LEN = 50

# PyTorch 모델 로드
model_path = 'C:/Users/ITSC/Desktop/Project/WECANDO/final/wecando/static/wecando/model/bert_gold_model4.pth'
model_eng = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=6)
# 모델을 CPU에서 불러오기
model_eng.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model_eng.eval()

# 데이터 토큰화
tokenizer_eng = BertTokenizer.from_pretrained('bert-base-uncased')



def bert_tokenizer(sent, MAX_LEN):
    encoded_dict = tokenizer_ko.encode_plus(
        text=sent,
        add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
        max_length=MAX_LEN,  # Pad & truncate all sentences.
        pad_to_max_length=True,
        return_attention_mask=True  # Construct attn. masks.
    )
    input_id = encoded_dict['input_ids']
    attention_mask = encoded_dict[
        'attention_mask']  # And its attention mask (simply differentiates padding from non-padding).
    token_type_id = encoded_dict['token_type_ids']  # differentiate two sentences
    return input_id, attention_mask, token_type_id



class WecandoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wecando'

    # 사용자 정의 모델 정의
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

    model_ko = CustomBERTModel(6)  # 클래스 개수

    # 모델에 적절한 입력 데이터 제공하여 내부 구조 초기화
    test_input = tokenizer_ko.encode_plus("테스트 문장", return_tensors='tf', padding='max_length', max_length=128,
                                       truncation=True)
    model_ko(test_input['input_ids'], attention_mask=test_input['attention_mask'],
          token_type_ids=test_input['token_type_ids'])

    # 가중치 로드
    model_ko.load_weights('C:/Users/ITSC/Desktop/Project/WECANDO/final/wecando/static/wecando/model/1120_saved_model_10epoch.h5')

    def sentence_convert_data(data):
        tokens, masks, segment = [], [], []
        input_id, attention_mask, token_type_id = bert_tokenizer(data, MAX_LEN)
        tokens.append(input_id)
        masks.append(attention_mask)
        segment.append(token_type_id)
        tokens = np.array(tokens, dtype=int)
        masks = np.array(masks, dtype=int)
        segments = np.array(segment, dtype=int)
        return [tokens, masks, segments]

# 예측 함수
    def predict_emotion(text):

        text1 = text.replace('[^A-Za-z0-9가-힣 ]', '')
        text2 = text1.lower()

        inputs = tokenizer_eng(text2, return_tensors="pt",add_special_tokens=True, padding=True, truncation=True, max_length=512)
        emotion_labels = [0,1,2,3,4,5]
        with torch.no_grad():
            outputs = model_eng(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        return emotion_labels[prediction]
