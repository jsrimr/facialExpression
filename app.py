import streamlit as st
import requests
from PIL import Image
import io

# API 관련 설정
API_URL = "https://www.ailabapi.com/api/portrait/effects/emotion-editor"
API_KEY = "AEq1CAeF4bYWDVOlni6S9iDFaRdTwz0yymoM9gLN1jj27gUZJncUML0Qvs3hmbSN"  # 발급받은 API 키 입력

# 표정 매핑 딕셔너리: 선택한 문자열을 숫자 코드로 변환합니다.
expression_mapping = {
    "Big laugh": 0,
    "Pouting": 1,
    "Feel sad": 2,
    "Smile": 3,
    "Dimple Smile": 10,
    "Pear Dimple Smile": 11,
    "Big Grin": 12,
    "Standard Grin": 13,
    "Cool Pose": 14,
    "Sad": 15,
    "Forced Smile": 16,
    "Opening eyes": 100
}

def change_expression(file_obj, expression_code: int) -> Image.Image:
    """
    업로드된 파일 객체와 숫자로 변환된 표정 코드를 API에 전송하여
    변환된 이미지를 반환합니다.
    """
    # 파일 객체의 포인터를 맨 앞으로 돌려 API에 올바른 파일 데이터를 전달합니다.
    file_obj.seek(0)
    
    files = [
        ('image_target', ('file', file_obj, 'application/octet-stream'))
    ]
    payload = {
        'service_choice': expression_code
    }
    headers = {
        'ailabapi-api-key': API_KEY
    }
    
    response = requests.request("POST", API_URL, headers=headers, data=payload, files=files)
    
    if response.status_code == 200:
        try:
            # API 응답 데이터를 PIL 이미지로 변환합니다.
            result_img = Image.open(io.BytesIO(response.content))
            return result_img
        except Exception as e:
            st.error(f"API 응답 이미지를 처리하는 중 오류 발생: {e}")
            return None
    else:
        st.error(f"API 호출 중 에러 발생: {response.status_code}\n{response.text}")
        return None

# Streamlit UI 구성
st.title("얼굴 표정 변환기")
st.write("원하는 표정으로 얼굴 사진을 변환합니다.")

# 이미지 업로드 (이미 파일 객체 형태로 제공됨)
uploaded_file = st.file_uploader("얼굴 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

# 사용자가 선택할 수 있는 표정 옵션 (문자열)
selected_expression = st.selectbox("표정을 선택하세요", list(expression_mapping.keys()))

if st.button("표정 변경"):
    if uploaded_file is None:
        st.warning("먼저 이미지를 업로드하세요.")
    else:
        # 원본 이미지 표시 (파일 객체의 포인터를 맨 앞에 위치시키기)
        uploaded_file.seek(0)
        original_img = Image.open(uploaded_file)
        st.image(original_img, caption="원본 이미지", use_column_width=True)
        
        # 선택한 표정을 숫자 코드로 변환
        expression_code = expression_mapping[selected_expression]
        
        with st.spinner("표정 변경 중..."):
            result_image = change_expression(uploaded_file, expression_code)
        
        if result_image:
            st.image(result_image, caption="변경된 이미지", use_column_width=True)
