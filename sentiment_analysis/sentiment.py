#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
감성 분석 모듈
간단한 키워드 기반 감성 분석 (KoBERT 대신 경량화)
"""

import re
import json
import pandas as pd
from collections import Counter

class SentimentAnalyzer:
    def __init__(self):
        # 긍정/부정 키워드 사전 (한국어)
        self.positive_words = {
            '좋다', '훌륭하다', '우수하다', '성공', '발전', '성장', '상승', '증가', '개선', '향상',
            '긍정적', '효과적', '유익', '도움', '혜택', '이익', '수익', '호조', '활성화', '회복',
            '안정', '확대', '강화', '개선', '발달', '진전', '진보', '번영', '풍요', '만족',
            '기대', '희망', '신뢰', '믿음', '확신', '낙관', '밝다', '밝은', '좋은', '훌륭한'
        }
        
        self.negative_words = {
            '나쁘다', '문제', '위험', '위기', '하락', '감소', '악화', '부정적', '손실', '손해',
            '피해', '타격', '충격', '우려', '걱정', '불안', '어려움', '곤란', '어렵다', '힘들다',
            '실패', '좌절', '침체', '둔화', '악영향', '부작용', '문제점', '단점', '취약', '불리',
            '비관', '절망', '실망', '후회', '분노', '화', '짜증', '스트레스', '압박', '부담'
        }
    
    def clean_text(self, text):
        """텍스트 전처리"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수문자 제거 (한글, 영문, 숫자, 공백만 남김)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def analyze_sentiment(self, text):
        """단일 텍스트의 감성 분석"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0, 'positive_count': 0, 'negative_count': 0}
        
        cleaned_text = self.clean_text(text).lower()
        
        # 긍정/부정 키워드 카운트
        positive_count = 0
        negative_count = 0
        
        for word in self.positive_words:
            positive_count += cleaned_text.count(word)
        
        for word in self.negative_words:
            negative_count += cleaned_text.count(word)
        
        # 감성 점수 계산 (-1 ~ 1)
        total_count = positive_count + negative_count
        if total_count == 0:
            sentiment = 'neutral'
            score = 0.0
        else:
            score = (positive_count - negative_count) / total_count
            if score > 0.1:
                sentiment = 'positive'
            elif score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def analyze_articles(self, articles):
        """여러 기사의 감성 분석"""
        results = []
        sentiment_summary = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in articles:
            # 제목과 본문을 합쳐서 분석
            title = article.get('title', '')
            content = article.get('content', '')
            summary = article.get('summary', '')
            
            combined_text = f"{title} {summary} {content}"
            
            sentiment_result = self.analyze_sentiment(combined_text)
            
            # 기사 정보에 감성 분석 결과 추가
            article_with_sentiment = article.copy()
            article_with_sentiment['sentiment'] = sentiment_result
            
            results.append(article_with_sentiment)
            
            # 전체 감성 요약 업데이트
            sentiment_summary[sentiment_result['sentiment']] += 1
        
        return results, sentiment_summary
    
    def get_sentiment_statistics(self, analyzed_articles):
        """감성 분석 통계 생성"""
        if not analyzed_articles:
            return {}
        
        total_articles = len(analyzed_articles)
        positive_count = sum(1 for article in analyzed_articles if article['sentiment']['sentiment'] == 'positive')
        negative_count = sum(1 for article in analyzed_articles if article['sentiment']['sentiment'] == 'negative')
        neutral_count = sum(1 for article in analyzed_articles if article['sentiment']['sentiment'] == 'neutral')
        
        # 평균 감성 점수
        avg_score = sum(article['sentiment']['score'] for article in analyzed_articles) / total_articles
        
        statistics = {
            'total_articles': total_articles,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': round(positive_count / total_articles * 100, 1),
            'negative_ratio': round(negative_count / total_articles * 100, 1),
            'neutral_ratio': round(neutral_count / total_articles * 100, 1),
            'average_score': round(avg_score, 3),
            'overall_sentiment': 'positive' if avg_score > 0.1 else 'negative' if avg_score < -0.1 else 'neutral'
        }
        
        return statistics
    
    def save_sentiment_analysis(self, analyzed_articles, filename="sentiment_analysis.json"):
        """감성 분석 결과 저장"""
        try:
            data = {
                'articles': analyzed_articles,
                'statistics': self.get_sentiment_statistics(analyzed_articles),
                'analysis_date': str(pd.Timestamp.now())
            }
            
            filepath = f"data/{filename}"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return filepath
            
        except Exception as e:
            print(f"❌ 감성 분석 결과 저장 오류: {e}")
            return None

if __name__ == "__main__":
    # 개발용 테스트 코드
    pass