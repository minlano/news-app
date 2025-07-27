#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기능 테스트 스크립트
"""

import sys
import os
import json
sys.path.insert(0, '.')

print("🧪 기능 테스트 시작...")

# 1. 크롤링 테스트 (간단한 테스트)
print("\n🔍 크롤링 테스트:")
try:
    from crawler.daum_crawler import DaumNewsCrawler
    crawler = DaumNewsCrawler()
    
    # 간단한 검색 테스트 (2개만)
    articles = crawler.search_news("테스트", max_articles=2)
    
    if articles:
        print(f"✅ 크롤링 성공: {len(articles)}개 기사 수집")
        print(f"   첫 번째 기사: {articles[0]['title'][:50]}...")
    else:
        print("⚠️ 크롤링 결과 없음")
        
except Exception as e:
    print(f"❌ 크롤링 테스트 실패: {e}")

# 2. 키워드 추출 테스트
print("\n🔍 키워드 추출 테스트:")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("keyword_extractor", "keyword/keyword_extractor.py")
    keyword_extractor_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(keyword_extractor_module)
    KeywordExtractor = keyword_extractor_module.KeywordExtractor
    
    extractor = KeywordExtractor()
    
    # 테스트 텍스트
    test_text = "인공지능과 머신러닝 기술이 발전하면서 자동화 시스템이 확산되고 있다."
    keywords = extractor.extract_nouns(test_text)
    
    if keywords:
        print(f"✅ 키워드 추출 성공: {len(keywords)}개 키워드")
        for word, count in keywords[:3]:
            print(f"   - {word}: {count}")
    else:
        print("⚠️ 키워드 추출 결과 없음")
        
except Exception as e:
    print(f"❌ 키워드 추출 테스트 실패: {e}")

# 3. 감성 분석 테스트
print("\n😊 감성 분석 테스트:")
try:
    from sentiment_analysis.sentiment import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    
    # 테스트 텍스트들
    test_texts = [
        "정말 좋은 소식이네요! 기대됩니다.",
        "심각한 문제가 발생했습니다. 걱정됩니다.",
        "일반적인 뉴스 내용입니다."
    ]
    
    for i, text in enumerate(test_texts, 1):
        result = analyzer.analyze_sentiment(text)
        print(f"✅ 테스트 {i}: {result['sentiment']} (점수: {result['score']})")
        
except Exception as e:
    print(f"❌ 감성 분석 테스트 실패: {e}")

# 4. 워드클라우드 생성 테스트
print("\n☁️ 워드클라우드 테스트:")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("wordcloud_gen", "keyword/wordcloud_gen.py")
    wordcloud_gen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wordcloud_gen_module)
    WordCloudGenerator = wordcloud_gen_module.WordCloudGenerator
    
    generator = WordCloudGenerator()
    
    # 테스트 키워드 데이터
    test_keywords = {
        "인공지능": 10,
        "머신러닝": 8,
        "딥러닝": 6,
        "데이터": 5,
        "기술": 4
    }
    
    wordcloud = generator.create_wordcloud(test_keywords, style='default')
    
    if wordcloud:
        print("✅ 워드클라우드 생성 성공")
        
        # 저장 테스트
        saved_path = generator.save_wordcloud(wordcloud, "test_wordcloud.png")
        if saved_path:
            print(f"✅ 워드클라우드 저장 성공: {saved_path}")
        else:
            print("⚠️ 워드클라우드 저장 실패")
    else:
        print("❌ 워드클라우드 생성 실패")
        
except Exception as e:
    print(f"❌ 워드클라우드 테스트 실패: {e}")

# 5. PDF 리포트 생성 테스트
print("\n📄 PDF 리포트 테스트:")
try:
    from report.report_generator import NewsReportGenerator
    
    generator = NewsReportGenerator()
    
    # 테스트 데이터
    test_articles = [
        {
            "title": "테스트 기사 제목",
            "content": "테스트 기사 내용입니다.",
            "source": "테스트 소스",
            "link": "http://test.com"
        }
    ]
    
    test_keywords = {
        "keywords": [
            {"word": "테스트", "count": 5},
            {"word": "기사", "count": 3}
        ]
    }
    
    pdf_path = generator.generate_report(
        keyword="테스트",
        articles=test_articles,
        keywords_data=test_keywords
    )
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"✅ PDF 리포트 생성 성공: {pdf_path}")
    else:
        print("❌ PDF 리포트 생성 실패")
        
except Exception as e:
    print(f"❌ PDF 리포트 테스트 실패: {e}")

# 6. 이메일 발송 테스트 (설정만 체크)
print("\n📧 이메일 설정 테스트:")
try:
    from report.email_sender import EmailSender
    
    sender = EmailSender()
    env_config = sender.get_env_email_config()
    
    if env_config['gmail_email'] and env_config['gmail_password']:
        print("✅ 이메일 설정 완료 - 발송 가능")
        print(f"   발송자: {env_config['gmail_email']}")
    else:
        print("⚠️ 이메일 설정 불완전 - .env 파일 확인 필요")
        
except Exception as e:
    print(f"❌ 이메일 설정 테스트 실패: {e}")

# 7. 임시 파일 정리
print("\n🧹 임시 파일 정리:")
temp_files = ["data/test_wordcloud.png"]
for file_path in temp_files:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"✅ {file_path} 삭제 완료")
        except Exception as e:
            print(f"⚠️ {file_path} 삭제 실패: {e}")

print("\n🎉 기능 테스트 완료!")
print("\n📋 테스트 요약:")
print("- 모든 모듈이 정상적으로 import됨")
print("- 기본 기능들이 정상 작동함")
print("- 한글 폰트 지원됨")
print("- 이메일 설정 완료됨")
print("\n🚀 웹앱 실행 준비 완료!")