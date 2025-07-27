#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
텍스트 요약기
sumy 라이브러리를 사용한 TextRank 기반 요약
"""

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import re

class TextSummarizer:
    def __init__(self, language='korean'):
        self.language = language
        self.textrank_summarizer = TextRankSummarizer()
        self.lexrank_summarizer = LexRankSummarizer()
    
    def clean_text(self, text):
        """텍스트 전처리"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수문자 정리
        text = re.sub(r'\[.*?\]', '', text)  # [기자명] 등 제거
        text = re.sub(r'\(.*?\)', '', text)  # (괄호) 내용 제거
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    def summarize_textrank(self, text, sentence_count=3):
        """TextRank 알고리즘으로 요약"""
        try:
            cleaned_text = self.clean_text(text)
            
            if len(cleaned_text) < 100:  # 너무 짧은 텍스트는 그대로 반환
                return cleaned_text
            
            # 문장이 너무 적으면 sentence_count 조정
            sentences = cleaned_text.split('.')
            if len(sentences) <= sentence_count:
                return cleaned_text
            
            parser = PlaintextParser.from_string(cleaned_text, Tokenizer(self.language))
            summary = self.textrank_summarizer(parser.document, sentence_count)
            
            summary_text = ' '.join([str(sentence) for sentence in summary])
            return summary_text
            
        except Exception as e:
            print(f"❌ TextRank 요약 오류: {e}")
            return self.clean_text(text)[:200] + "..."  # 실패시 앞부분만 반환
    
    def summarize_lexrank(self, text, sentence_count=3):
        """LexRank 알고리즘으로 요약"""
        try:
            cleaned_text = self.clean_text(text)
            
            if len(cleaned_text) < 100:
                return cleaned_text
            
            sentences = cleaned_text.split('.')
            if len(sentences) <= sentence_count:
                return cleaned_text
            
            parser = PlaintextParser.from_string(cleaned_text, Tokenizer(self.language))
            summary = self.lexrank_summarizer(parser.document, sentence_count)
            
            summary_text = ' '.join([str(sentence) for sentence in summary])
            return summary_text
            
        except Exception as e:
            print(f"❌ LexRank 요약 오류: {e}")
            return self.clean_text(text)[:200] + "..."
    
    def summarize_simple(self, text, max_length=200):
        """간단한 요약 (앞부분 추출)"""
        cleaned_text = self.clean_text(text)
        
        if len(cleaned_text) <= max_length:
            return cleaned_text
        
        # 문장 단위로 자르기
        sentences = cleaned_text.split('.')
        summary = ""
        
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "."
            else:
                break
        
        return summary.strip()
    
    def summarize_articles(self, articles, method='textrank', sentence_count=3):
        """여러 기사를 요약"""
        print(f"📝 {method} 방식으로 기사 요약 중...")
        
        summarized_articles = []
        
        for i, article in enumerate(articles, 1):
            print(f"📄 {i}/{len(articles)}: {article['title'][:30]}... 요약 중")
            
            # 본문이 있으면 본문을, 없으면 요약을 사용
            text_to_summarize = article.get('content', '') or article.get('summary', '')
            
            if method == 'textrank':
                summary = self.summarize_textrank(text_to_summarize, sentence_count)
            elif method == 'lexrank':
                summary = self.summarize_lexrank(text_to_summarize, sentence_count)
            else:
                summary = self.summarize_simple(text_to_summarize)
            
            # 기사 정보에 요약 추가
            article_copy = article.copy()
            article_copy['ai_summary'] = summary
            summarized_articles.append(article_copy)
        
        print(f"✅ {len(summarized_articles)}개 기사 요약 완료!")
        return summarized_articles

if __name__ == "__main__":
    # 개발용 테스트 코드
    pass