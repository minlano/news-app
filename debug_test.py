#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디버깅 테스트 스크립트
"""

import sys
import os

print("🔍 시스템 디버깅 시작...")
print(f"Python 버전: {sys.version}")
print(f"현재 디렉토리: {os.getcwd()}")

# 1. 필수 라이브러리 체크
print("\n📦 라이브러리 체크:")
libraries = [
    ('requests', 'requests'),
    ('beautifulsoup4', 'bs4'),
    ('streamlit', 'streamlit'),
    ('pandas', 'pandas'),
    ('matplotlib', 'matplotlib'),
    ('wordcloud', 'wordcloud'),
    ('sumy', 'sumy'),
    ('fpdf2', 'fpdf'),
    ('python-dotenv', 'dotenv')
]

for lib_name, import_name in libraries:
    try:
        __import__(import_name)
        print(f"✅ {lib_name} 설치됨")
    except ImportError as e:
        print(f"❌ {lib_name} 설치 필요: {e}")

# 2. 모듈 import 테스트
print("\n🔧 모듈 import 테스트:")
sys.path.insert(0, '.')

modules_to_test = [
    ('crawler.daum_crawler', 'DaumNewsCrawler'),
    ('summarizer.text_summarizer', 'TextSummarizer'),
    ('sentiment_analysis.sentiment', 'SentimentAnalyzer'),
    ('report.report_generator', 'NewsReportGenerator'),
    ('report.email_sender', 'EmailSender')
]

for module_path, class_name in modules_to_test:
    try:
        module = __import__(module_path, fromlist=[class_name])
        getattr(module, class_name)
        print(f"✅ {class_name} import 성공")
    except Exception as e:
        print(f"❌ {class_name} import 실패: {e}")

# 3. 특별 모듈 테스트 (importlib 사용)
print("\n🎯 특별 모듈 테스트:")
try:
    import importlib.util
    
    # KeywordExtractor 테스트
    spec = importlib.util.spec_from_file_location("keyword_extractor", "keyword/keyword_extractor.py")
    keyword_extractor_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(keyword_extractor_module)
    print("✅ KeywordExtractor import 성공")
    
    # WordCloudGenerator 테스트
    spec = importlib.util.spec_from_file_location("wordcloud_gen", "keyword/wordcloud_gen.py")
    wordcloud_gen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wordcloud_gen_module)
    print("✅ WordCloudGenerator import 성공")
    
except Exception as e:
    print(f"❌ 특별 모듈 import 실패: {e}")

# 4. 폴더 구조 체크
print("\n📁 폴더 구조 체크:")
required_folders = ['app', 'crawler', 'summarizer', 'keyword', 'sentiment_analysis', 'report']
for folder in required_folders:
    if os.path.exists(folder):
        print(f"✅ {folder}/ 폴더 존재")
    else:
        print(f"❌ {folder}/ 폴더 없음")

# 5. data 폴더 체크
if os.path.exists('data'):
    print("✅ data/ 폴더 존재")
    files = os.listdir('data')
    if files:
        print(f"   📄 파일들: {files}")
    else:
        print("   📭 빈 폴더")
else:
    print("❌ data/ 폴더 없음 - 생성 필요")
    try:
        os.makedirs('data')
        print("✅ data/ 폴더 생성 완료")
    except Exception as e:
        print(f"❌ data/ 폴더 생성 실패: {e}")

# 6. .env 파일 체크
print("\n🔐 환경 변수 체크:")
if os.path.exists('.env'):
    print("✅ .env 파일 존재")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        gmail_email = os.getenv('GMAIL_EMAIL')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if gmail_email:
            print(f"✅ GMAIL_EMAIL 설정됨: {gmail_email}")
        else:
            print("⚠️ GMAIL_EMAIL 설정 안됨")
            
        if gmail_password:
            print("✅ GMAIL_APP_PASSWORD 설정됨")
        else:
            print("⚠️ GMAIL_APP_PASSWORD 설정 안됨")
            
    except Exception as e:
        print(f"❌ .env 파일 로드 실패: {e}")
else:
    print("⚠️ .env 파일 없음 - 이메일 발송 기능 사용 불가")

# 7. 한글 폰트 체크
print("\n🎨 한글 폰트 체크:")
font_paths = [
    'C:/Windows/Fonts/malgun.ttf',
    'C:/Windows/Fonts/gulim.ttc',
    'C:/Windows/Fonts/batang.ttc'
]

for font_path in font_paths:
    if os.path.exists(font_path):
        print(f"✅ 한글 폰트 발견: {font_path}")
        break
else:
    print("⚠️ 한글 폰트를 찾을 수 없음 - PDF/워드클라우드에서 한글 표시 문제 가능")

print("\n🎉 디버깅 완료!")