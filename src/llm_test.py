from dotenv import load_dotenv
from google import genai

# ① .env 파일을 읽어서 환경변수로 올리기
load_dotenv()

# ② 클라이언트 만들기 (GEMINI_API_KEY를 자동으로 찾음)
client = genai.Client()

# ③ 요청 보내기
interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="나는 요즘 너무 힘들어"
)

# ④ 응답 텍스트만 출력
print(interaction.output_text)