import numpy as np
import pandas as pd
import tensorflow as tf
from transformers import AutoTokenizer

import os

BATCH_SIZE = 1
MAX_LEN = 192
MODEL = "jplu/tf-xlm-roberta-base"
#ROOT_DIR = os.path.abspath("../../")
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


def inference(test_file, sensitivity):

    model, tokenizer = infer()

    load_file = pd.read_csv(test_file)

    load_file_needed = load_file[["id", "content"]]

    x_test = regular_encode(load_file_needed.content.values, tokenizer, maxlen=MAX_LEN)

    test_dataset = tf.data.Dataset.from_tensor_slices(x_test).batch(BATCH_SIZE)

    pred = model.predict(test_dataset, verbose=1)

    #    print("prediction score", pred)

    toxic_comment, non_toxic_comment = 0, 0
    output = []

    for i in pred:
        if i > (sensitivity / 100):  # 0.6:
            toxic_comment += 1
        else:
            non_toxic_comment += 1

    output.append(toxic_comment)
    output.append(non_toxic_comment)
    return output


# T_COUNT = 0
# NT_COUNT = 0
def inference_v2(comment_text, sensitivity):
    # global T_COUNT
    # global NT_COUNT

    comment_text = [comment_text]
    x_test = regular_encode(comment_text, TOKENIZER, maxlen=MAX_LEN)
    test_dataset = tf.data.Dataset.from_tensor_slices(x_test).batch(10)
    pred = LOADED_MODEL.predict(test_dataset, verbose=1)

    # if pred[0] > (sensitivity / 100):
    #     T_COUNT += 1
    # else:
    #     NT_COUNT +=1

    # return T_COUNT, NT_COUNT, pred[0]
    return pred[0][0]


def load_model():
    global LOADED_MODEL
    global TOKENIZER
    if (LOADED_MODEL is None) and (TOKENIZER is None):
        LOADED_MODEL, TOKENIZER = infer()