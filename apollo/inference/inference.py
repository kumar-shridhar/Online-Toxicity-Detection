import numpy as np
import tensorflow as tf
from transformers import AutoTokenizer

import os

BATCH_SIZE = 1
MAX_LEN = 192
MODEL = "jplu/tf-xlm-roberta-base"
MODEL_PATH = os.path.abspath("./apollo/inference/new_toxic_model")

LOADED_MODEL = None
TOKENIZER = None

def infer():
    model = tf.keras.models.load_model(MODEL_PATH )
    print(model)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)

    return model, tokenizer


def regular_encode(texts, tokenizer, maxlen=512):
    enc_di = tokenizer.batch_encode_plus(
        texts,
        return_attention_masks=False,
        return_token_type_ids=False,
        pad_to_max_length=True,
        max_length=maxlen,
    )

    return np.array(enc_di["input_ids"])


def inference_v2(comment_text, sensitivity):
    # global T_COUNT
    # global NT_COUNT

    comment_text = [comment_text]
    x_test = regular_encode(comment_text, TOKENIZER, maxlen=MAX_LEN)
    test_dataset = tf.data.Dataset.from_tensor_slices(x_test).batch(10)
    pred = LOADED_MODEL.predict(test_dataset, verbose=1)

    return pred[0][0]


def load_model():
    global LOADED_MODEL
    global TOKENIZER
    if (LOADED_MODEL is None) and (TOKENIZER is None):
        LOADED_MODEL, TOKENIZER = infer()
    print("********** MODEL IS NOW LOADED AND THE APP IS READY FOR USE ****************")