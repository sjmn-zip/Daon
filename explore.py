import pandas as pd

# json 파일 읽기
df = pd.read_json("data/감성대화말뭉치(최종데이터)_Training.json")

# 앞 5줄 미리보기
print(df.head())

# 크기 확인 (행, 열)
print(df.shape)

# 컬럼(열) 이름 확인
print(df.columns)

# 첫 번째 행의 profile 딕셔너리 전체를 펼쳐보기
print("=== profile 구조 ===")
print(df.loc[0, "profile"])

print("=== talk 구조 ===")
print(df.loc[0, "talk"])