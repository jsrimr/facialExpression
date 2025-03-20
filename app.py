import streamlit as st
import requests
from PIL import Image
import io
import base64

# API 관련 설정
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AILAB_API_KEY")
EXPRESSION_API_URL = "https://www.ailabapi.com/api/portrait/effects/emotion-editor"
AGE_API_URL = "https://www.ailabapi.com/api/portrait/effects/face-attribute-editing"

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
    "Opening eyes": 100,
}


def change_expression(file_obj, expression_code: int) -> Image.Image:
    """
    업로드된 파일 객체와 숫자로 변환된 표정 코드를 API에 전송하여,
    응답으로 받은 JSON 내의 base64 인코딩된 이미지를 디코딩하여 반환합니다.
    """
    file_obj.seek(0)
    files = [("image_target", ("file", file_obj, "application/octet-stream"))]
    payload = {"service_choice": expression_code}
    headers = {"ailabapi-api-key": API_KEY}

    response = requests.request(
        "POST", EXPRESSION_API_URL, headers=headers, data=payload, files=files
    )

    if response.status_code == 200:
        try:
            json_data = response.json()
            if json_data.get("error_code", 1) != 0:
                st.error(f"API Error: {json_data.get('error_msg', 'Unknown error')}")
                return None
            base64_image = json_data["data"]["image"]
            image_data = base64.b64decode(base64_image)
            result_img = Image.open(io.BytesIO(image_data))
            return result_img
        except Exception as e:
            st.error(f"응답 처리 중 오류 발생: {e}")
            return None
    else:
        st.error(f"API 호출 중 에러 발생: {response.status_code}\n{response.text}")
        return None


def change_age(file_obj, action_type: str = "TO_OLD") -> Image.Image:
    """
    업로드된 파일 객체와 액션 타입('TO_OLD' 등)을 API에 전송하여,
    응답으로 받은 JSON 내의 base64 인코딩된 이미지를 디코딩하여 반환합니다.
    현재 지원하는 액션 타입은 'TO_OLD' (노화 효과)입니다.
    """
    file_obj.seek(0)
    files = [("image", ("file", file_obj, "application/octet-stream"))]
    payload = {"action_type": action_type}
    headers = {"ailabapi-api-key": API_KEY}
    response = requests.post(AGE_API_URL, headers=headers, data=payload, files=files)

    if response.status_code == 200:
        try:
            json_data = response.json()
            if json_data.get("error_code", 1) != 0:
                st.error(f"API Error: {json_data.get('error_msg', 'Unknown error')}")
                return None
            base64_image = json_data["result"]["image"]
            image_data = base64.b64decode(base64_image)
            result_img = Image.open(io.BytesIO(image_data))
            return result_img
        except Exception as e:
            st.error(f"응답 처리 중 오류 발생: {e}")
            return None
    else:
        st.error(f"API 호출 중 에러 발생: {response.status_code}\n{response.text}")
        return None


# Streamlit UI 구성
st.title("얼굴 표정 및 나이 변환 서비스")
st.write(
    "업로드한 얼굴 사진에 웃는 표정, 노화 효과, 그리고 두 효과를 동시에 적용할 수 있습니다."
)

uploaded_file = st.file_uploader(
    "얼굴 사진을 업로드하세요", type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    # 업로드한 이미지 미리보기
    try:
        original_img = Image.open(uploaded_file)
    except Exception as e:
        st.error(f"이미지를 여는 중 오류 발생: {e}")
        st.stop()
    st.image(original_img, caption="원본 이미지", use_column_width=True)

    if st.button("start"):
        # 업로드한 파일의 바이트 데이터를 읽어 각 API 호출에 사용할 별도의 BytesIO 객체 생성
        bytes_data = uploaded_file.getvalue()
        file_expr = io.BytesIO(bytes_data)  # 표정 변환용
        file_age = io.BytesIO(bytes_data)  # 노화 효과용

        with st.spinner("표정 및 나이 변환 중..."):
            # 웃는 표정으로 변환 (표정 API 사용: "Smile")
            result_expr = change_expression(file_expr, expression_mapping["Smile"])

            # 원본 이미지에 노화 효과 적용 (나이 API 사용)
            result_age = change_age(file_age, "TO_OLD")

            # 웃는 표정으로 변환한 이미지에 노화 효과 추가
            if result_expr is not None:
                # PIL 이미지를 BytesIO 객체로 변환하여 age API에 전달
                img_bytes = io.BytesIO()
                result_expr.save(img_bytes, format="JPEG")
                img_bytes.seek(0)
                result_expr_age = change_age(img_bytes, "TO_OLD")
            else:
                result_expr_age = None

        # 사분할 화면 레이아웃 생성
        col1, col2 = st.columns(2)
        with col1:
            st.image(original_img, caption="Input Image", use_container_width=True)
        with col2:
            if result_expr:
                st.image(
                    result_expr, caption="Smile Expression", use_container_width=True
                )
            else:
                st.error("표정 변환 실패")

        col3, col4 = st.columns(2)
        with col3:
            if result_age:
                st.image(result_age, caption="Aged Image", use_container_width=True)
            else:
                st.error("노화 변환 실패")
        with col4:
            if result_expr_age:
                st.image(
                    result_expr_age,
                    caption="Smile + Aged Image",
                    use_container_width=True,
                )
            else:
                st.error("표정 및 노화 변환 실패")
else:
    st.info("먼저 이미지를 업로드하세요.")
