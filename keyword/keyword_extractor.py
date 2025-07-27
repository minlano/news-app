#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
키워드 추출기
KoNLPy Okt를 사용한 명사 추출
"""

import re
import json
from collections import Counter

class KeywordExtractor:
    def __init__(self):
        # KoNLPy 대신 간단한 정규식 기반 키워드 추출 사용
        pass
        
        # 불용어 리스트 (제외할 단어들)
        self.stopwords = {
            '것', '수', '등', '때', '곳', '점', '개', '명', '번', '차', '년', '월', '일',
            '이', '그', '저', '의', '를', '에', '가', '은', '는', '이다', '있다', '하다',
            '되다', '같다', '다른', '새로운', '많은', '좋은', '큰', '작은', '높은', '낮은',
            '기자', '뉴스', '기사', '보도', '취재', '인터뷰', '발표', '설명', '말',
            '오늘', '어제', '내일', '이번', '다음', '지난', '최근', '현재', '앞으로',
            '서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종',
            '한국', '우리나라', '국내', '전국', '지역', '지방', '수도권', '비수도권'
        }
    
    def clean_text(self, text):
        """텍스트 전처리"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수문자 제거 (한글, 영문, 숫자만 남김)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_nouns(self, text, min_length=2):
        """간단한 정규식 기반 키워드 추출"""
        try:
            cleaned_text = self.clean_text(text)
            
            # 한글 단어 추출 (2글자 이상)
            korean_words = re.findall(r'[가-힣]{2,}', cleaned_text)
            
            # 필터링: 길이, 불용어 제거
            filtered_words = []
            for word in korean_words:
                if (len(word) >= min_length and 
                    word not in self.stopwords and
                    not word.isdigit()):
                    filtered_words.append(word)
            
            return filtered_words
            
        except Exception as e:
            print(f"❌ 키워드 추출 오류: {e}")
            return []
    
    def get_keyword_frequency(self, texts, top_n=20):
        """여러 텍스트에서 키워드 빈도 계산"""
        all_nouns = []
        
        for text in texts:
            nouns = self.extract_nouns(text)
            all_nouns.extend(nouns)
        
        # 빈도 계산
        counter = Counter(all_nouns)
        
        # 상위 N개 키워드 반환
        top_keywords = counter.most_common(top_n)
        
        return top_keywords
    
    def extract_keywords_from_articles(self, articles, top_n=30):
        """기사들에서 키워드 추출"""
        print(f"🔍 기사에서 키워드 추출 중...")
        
        # 모든 텍스트 수집 (제목 + 요약 + 본문)
        all_texts = []
        
        for article in articles:
            # 제목
            title = article.get('title', '')
            # 요약 (AI 요약이 있으면 우선, 없으면 원본 요약)
            summary = article.get('ai_summary', '') or article.get('summary', '')
            # 본문
            content = article.get('content', '')
            
            # 모든 텍스트 합치기
            combined_text = f"{title} {summary} {content}"
            all_texts.append(combined_text)
        
        # 키워드 빈도 계산
        keywords = self.get_keyword_frequency(all_texts, top_n)
        
        print(f"✅ 상위 {len(keywords)}개 키워드 추출 완료!")
        
        # 결과 출력
        print("\n📊 추출된 키워드:")
        for i, (keyword, count) in enumerate(keywords, 1):
            print(f"{i:2d}. {keyword} ({count}회)")
        
        return keywords
    
    def save_keywords(self, keywords, filename="keywords.json"):
        """키워드를 JSON 파일로 저장"""
        try:
            # 딕셔너리 형태로 변환
            keyword_dict = {
                'keywords': [{'word': word, 'count': count} for word, count in keywords],
                'total_keywords': len(keywords)
            }
            
            filepath = f"data/{filename}"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(keyword_dict, f, ensure_ascii=False, indent=2)
            
            print(f"💾 키워드가 {filepath}에 저장되었습니다.")
            return filepath
            
        except Exception as e:
            print(f"❌ 키워드 저장 오류: {e}")
            return None

if __name__ == "__main__":
    # 개발용 테스트 코드
    pass