import numpy as np
import pandas as pd
import tensorflow as tf
from transformers import AutoTokenizer

import os

BATCH_SIZE = 1
MAX_LEN = 192
MODEL = "jplu/tf-xlm-roberta-base"
ROOT_DIR = os.path.abspath("../../")
MODEL_PATH = os.path.join(ROOT_DIR, "apollo/inference/new_toxic_model")


def infer():
    if os.name == "nt":
        model = tf.keras.models.load_model(
            "C:\\AKRAM-Local\\github\\Apollo\\apollo\\inference\\new_toxic_model"
        )
    else:
        model = tf.keras.models.load_model(MODEL_PATH )
        #model = tf.keras.models.load_model(
        #    "/home/shri/git/mygit/APOLLO-1/apollo/inference/new_toxic_model"
        #)

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
