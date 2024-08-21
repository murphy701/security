import os
import shutil
import zipfile
from Crypto.Cipher import AES
from pathlib import Path
from Crypto.Util.Padding import unpad
import requests
import subprocess

# AES-128/ECB 복호화를 위한 키
key = b'dbcdcfghijklmaop'

# MobSF 설정
MOBSF_URL = 'http://localhost:8000'
API_KEY = 'YOUR_API_KEY'

# 서명 관련 설정 (apksigner 활용, 개인 환경에 맞게 변경)
KEYSTORE_PATH = 'my-release-key.jks'
KEYSTORE_PASSWORD = '123456'
KEY_ALIAS = 'my-key-alias'
KEY_PASSWORD = '123456'

# 복호화 처리 함수
def decrypt_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()

    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    with open(output_file, 'wb') as f:
        f.write(decrypted_data)

# apk 압축 해제 함수
def unzip_apk(apk_path, extract_to):
    with zipfile.ZipFile(apk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# apk 압축 함수
def zip_apk(directory, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory)
                zipf.write(file_path, arcname)

# APK 서명 함수
def sign_apk(apk_path, keystore_path, keystore_password, key_alias, key_password):
    apksigner_path = r'C:/Users/Laiika/AppData/Local/Android/Sdk/build-tools/34.0.0/apksigner.bat' #apksigner 경로로 변경
    cmd = [
        apksigner_path, 'sign',
        '--ks', keystore_path,
        '--ks-key-alias', key_alias,
        '--ks-pass', f'pass:{keystore_password}',
        '--key-pass', f'pass:{key_password}',
        '--out', f'signed_{apk_path}',
        apk_path
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"명령어 실행 중 오류 발생: {stderr}")
        raise subprocess.CalledProcessError(process.returncode, cmd)

    return f'signed_{apk_path}'

# MobSF에 APK 파일 업로드 함수
def upload_to_mobsf(apk_path):
    with open(apk_path, 'rb') as f:
        files = {'file': (os.path.basename(apk_path), f, 'application/vnd.android.package-archive')}
        headers = {'Authorization': API_KEY}
        response = requests.post(f'{MOBSF_URL}/api/v1/upload', files=files, headers=headers)
        response_json = response.json()
        print("API 응답:", response_json)  # 응답 출력
        if 'hash' in response_json:
            return response_json['hash'], response_json
        else:
            raise ValueError("API 응답에 'hash' 키가 없습니다.")

# MobSF에 APK 분석 요청 함수
def scan_with_mobsf(file_hash):
    headers = {'Authorization': API_KEY}
    data = {'hash': file_hash}
    response = requests.post(f'{MOBSF_URL}/api/v1/scan', headers=headers, data=data)
    return response.json()

# 메인 함수
def process_apk(apk_path, encrypted_dex_filename):
    base_name = Path(apk_path).stem
    extracted_dir = f'{base_name}_extracted'
    recompiled_apk = f'{base_name}_recompiled.apk'

    try:
        if os.path.exists(extracted_dir):
            print("기존 디렉토리 삭제")
            shutil.rmtree(extracted_dir)

        print("APK 파일 압축 해제")
        unzip_apk(apk_path, extracted_dir)

        encrypted_dex_path = os.path.join(extracted_dir, encrypted_dex_filename)
        decrypted_dex_path = os.path.join(extracted_dir, 'classes2.dex')
        if os.path.exists(encrypted_dex_path):
            print("DEX 파일 복호화")
            decrypt_file(encrypted_dex_path, decrypted_dex_path)    
        else:
            print(f"암호화된 DEX 파일을 찾을 수 없습니다: {encrypted_dex_path}")
            return

        print("APK 리패키징")
        zip_apk(extracted_dir, recompiled_apk)
        print(f"리패키징 완료, APK: {recompiled_apk}")

        print("APK 서명")
        signed_apk = sign_apk(recompiled_apk, KEYSTORE_PATH, KEYSTORE_PASSWORD, KEY_ALIAS, KEY_PASSWORD)
        print(f"서명 완료, APK: {signed_apk}")

        print("MobSF에 APK 파일 업로드")
        file_hash, upload_response = upload_to_mobsf(signed_apk)

        print("MobSF에 APK 분석 요청")
        analysis_result = scan_with_mobsf(file_hash)
        print("분석 결과:", analysis_result)
    except Exception as e:
        print(f"오류 발생: {str(e)}")


# 실행 예시
encrypted_dex_filename = 'kill-classes.dex'  # 파일 경로로 수정
process_apk('sample.apk', encrypted_dex_filename)  # 파일 경로로 수정
