from django.apps import AppConfig
import tensorflow as tf
import numpy as np
from transformers import TFBertModel, BertTokenizer

# BERT 토크나이저와 모델 로드
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
bert_model = TFBertModel.from_pretrained('bert-base-multilingual-cased')
MAX_LEN = 50


def bert_tokenizer(sent, MAX_LEN):
    encoded_dict = tokenizer.encode_plus(
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

    model = CustomBERTModel(6)  # 클래스 개수

    # 모델에 적절한 입력 데이터 제공하여 내부 구조 초기화
    test_input = tokenizer.encode_plus("테스트 문장", return_tensors='tf', padding='max_length', max_length=128,
                                       truncation=True)
    model(test_input['input_ids'], attention_mask=test_input['attention_mask'],
          token_type_ids=test_input['token_type_ids'])

    # 가중치 로드
    model.load_weights('C:/Users/82107/OneDrive/바탕 화면/final_project/final/wecando/static/wecando/model/1110_model_weights.h5')

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




