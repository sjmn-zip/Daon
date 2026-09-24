import pandas as pd

df = pd.read_json("data/감성대화말뭉치(최종데이터)_Training.json")


first_profile = df.loc[0, "profile"]
first_talk = df.loc[0, "talk"]


emotion_code = first_profile["emotion"]["type"]     
sentence = first_talk["content"]["HS01"]           

def code_to_emotion(emotion_code): 
    code_num = emotion_code[1]

    if code_num == "1":
        return "분노"
    elif code_num == "2":
        return  "슬픔"
    elif code_num =="3":
        return  "불안"
    elif code_num == "4":
        return  "상처"
    elif code_num == "5":
        return "당황"
    elif code_num == "6":
        return "기쁨"
    else:
        return "알 수 없음"

sentences = []
emotions = []

# 2. 5만 개 전부 반복
for i in range(len(df)):
    profile = df.loc[i, "profile"]
    talk = df.loc[i, "talk"]

    # i번 행에서 문장 꺼내기 (1단계에서 한 것과 동일)
    sentence = talk["content"]["HS01"]

    # i번 행에서 감정코드 꺼내서 → 함수로 변환
    emotion_code = profile["emotion"]["type"]
    emotion = code_to_emotion(emotion_code)      # 방금 만든 함수 사용!

    # 두 통에 담기
    sentences.append(sentence)
    emotions.append(emotion)

# 3. 표로 합치기
result = pd.DataFrame({"sentence": sentences, "emotion": emotions})

print(result["emotion"].value_counts())