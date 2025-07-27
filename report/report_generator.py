#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 리포트 생성 모듈
뉴스 분석 결과를 PDF로 생성
"""

from fpdf import FPDF
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class NewsReportGenerator:
    def __init__(self):
        # 한글 폰트 경로 설정
        self.korean_font_path = 'C:/Windows/Fonts/malgun.ttf'
        self.use_korean_font = os.path.exists(self.korean_font_path)
        
        # PDF 객체 생성 및 설정
        self.reset_pdf()
        
        print(f"한글 폰트 사용 가능: {self.use_korean_font}")
        if self.use_korean_font:
            print(f"✅ 한글 폰트 경로: {self.korean_font_path}")
        else:
            print("⚠️ 한글 폰트를 찾을 수 없습니다.")
    
    def reset_pdf(self):
        """PDF 객체를 새로 생성하고 폰트를 설정합니다."""
        self.pdf = FPDF()
        self.pdf.add_page()
        
        # 한글 폰트 추가
        if self.use_korean_font:
            try:
                self.pdf.add_font('korean', '', self.korean_font_path, uni=True)
                print("✅ 한글 폰트 로드 성공")
            except Exception as e:
                print(f"한글 폰트 로드 실패: {e}")
                self.use_korean_font = False
        
        # 기본 폰트를 한글 폰트로 설정
        if self.use_korean_font:
            self.pdf.set_font('korean', size=12)
        else:
            self.pdf.set_font('Arial', size=12)
    
    def safe_text_output(self, text, font_size=11, is_bold=False, center=False):
        """안전한 텍스트 출력 (한글 처리)"""
        try:
            # 한글이 포함된 경우 처리
            if any('\u3131' <= char <= '\uD7A3' for char in text):
                if self.use_korean_font:
                    # 한글 폰트 강제 설정
                    self.pdf.set_font('korean', '', font_size)
                    print(f"한글 폰트로 출력: {text[:20]}...")
                else:
                    # 한글 폰트가 없으면 영어로 대체
                    text = self.convert_korean_to_english(text)
                    self.pdf.set_font('Arial', '', font_size)
            else:
                # 영어 텍스트
                style = 'B' if is_bold else ''
                self.pdf.set_font('Arial', style, font_size)
            
            # 텍스트 출력
            if center:
                self.pdf.cell(0, 8, text, ln=True, align='C')
            else:
                self.pdf.cell(0, 8, text, ln=True)
            return True
            
        except Exception as e:
            print(f"텍스트 출력 오류: {e} - 텍스트: {text[:50]}")
            # 오류 발생 시 영어로 대체
            self.pdf.set_font('Arial', '', font_size)
            safe_text = '[Korean Text - Display Error]'
            if center:
                self.pdf.cell(0, 8, safe_text, ln=True, align='C')
            else:
                self.pdf.cell(0, 8, safe_text, ln=True)
            return False
    
    def convert_korean_to_english(self, text):
        """한글 텍스트를 영어로 변환 (간단한 매핑)"""
        # 기본적인 한글-영어 매핑
        korean_to_english = {
            '키워드': 'Keyword',
            '분석': 'Analysis',
            '뉴스': 'News',
            '기사': 'Article',
            '요약': 'Summary',
            '감성': 'Sentiment',
            '긍정': 'Positive',
            '부정': 'Negative',
            '중립': 'Neutral',
            '출처': 'Source',
            '제목': 'Title',
            '내용': 'Content',
            '시간': 'Time',
            '날짜': 'Date',
            '결과': 'Result',
            '통계': 'Statistics',
            '개수': 'Count',
            '비율': 'Ratio',
            '전체': 'Total',
            '상위': 'Top',
            '주요': 'Main',
            '최신': 'Latest'
        }
        
        # 한글이 포함된 경우 영어로 변환 시도
        result = text
        for korean, english in korean_to_english.items():
            result = result.replace(korean, english)
        
        # 여전히 한글이 있으면 완전히 영어로 대체
        if any('\u3131' <= char <= '\uD7A3' for char in result):
            if 'Keyword:' in text:
                return '[Korean Keyword]'
            elif 'Source:' in text or '출처:' in text:
                return '   Source: [Korean Source]'
            elif 'Summary:' in text or '요약:' in text:
                return '   Summary: [Korean Summary]'
            elif '. ' in text and '(' in text and 'times)' in text:
                # 키워드 목록 형태
                parts = text.split('. ', 1)
                if len(parts) == 2:
                    number = parts[0]
                    return f'{number}. [Korean Keyword] (times)'
            else:
                return '[Korean Text]'
        
        return result
    
    def add_title(self, keyword, article_count):
        """리포트 제목 추가"""
        self.pdf.set_font('Arial', 'B', 20)
        self.pdf.cell(0, 15, f'News Analysis Report', ln=True, align='C')
        
        # 키워드 안전 출력
        self.safe_text_output(f'Keyword: {keyword}', font_size=16, center=True)
        
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f'Analysis Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
        self.pdf.cell(0, 10, f'Total Articles: {article_count}', ln=True, align='C')
        self.pdf.ln(10)
    
    def add_summary_section(self, statistics):
        """요약 섹션 추가"""
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, 'Analysis Summary', ln=True)
        self.pdf.ln(5)
        
        # 기본 통계 - 안전한 출력 사용
        if 'total_articles' in statistics:
            self.safe_text_output(f'- Total Articles Analyzed: {statistics["total_articles"]}', font_size=11)
        
        # 감성 분석 결과 (있는 경우) - 안전한 출력 사용
        if 'positive_count' in statistics:
            self.safe_text_output(f'- Positive Articles: {statistics["positive_count"]} ({statistics["positive_ratio"]}%)', font_size=11)
            self.safe_text_output(f'- Negative Articles: {statistics["negative_count"]} ({statistics["negative_ratio"]}%)', font_size=11)
            self.safe_text_output(f'- Neutral Articles: {statistics["neutral_count"]} ({statistics["neutral_ratio"]}%)', font_size=11)
            self.safe_text_output(f'- Overall Sentiment: {statistics["overall_sentiment"].upper()}', font_size=11)
        
        self.pdf.ln(10)
    
    def safe_add_text(self, text, font_size=11, is_bold=False):
        """안전한 텍스트 추가 (한글 폰트 처리)"""
        try:
            # 한글이 포함된 경우 한글 폰트 사용
            if self.use_korean_font and any('\u3131' <= char <= '\uD7A3' for char in text):
                self.pdf.set_font('korean', '', font_size)
            else:
                style = 'B' if is_bold else ''
                self.pdf.set_font('Arial', style, font_size)
            
            self.pdf.cell(0, 8, text, ln=True)
            return True
        except Exception as e:
            # 폰트 오류 시 영어로 대체
            print(f"폰트 오류: {e}")
            self.pdf.set_font('Arial', '', font_size)
            self.pdf.cell(0, 8, '[Korean Text - Font Error]', ln=True)
            return False
    
    def add_keywords_section(self, keywords_data):
        """키워드 섹션 추가"""
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, 'Top Keywords', ln=True)
        self.pdf.ln(5)
        
        if keywords_data and 'keywords' in keywords_data:
            keywords = keywords_data['keywords'][:10]  # 상위 10개만
            
            for i, keyword in enumerate(keywords, 1):
                word = keyword['word']
                count = keyword['count']
                
                # 안전한 키워드 출력
                self.safe_text_output(f'{i:2d}. {word} ({count} times)', font_size=11)
        
        self.pdf.ln(10)
    
    def add_articles_section(self, articles):
        """기사 목록 섹션 추가"""
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, 'Article List', ln=True)
        self.pdf.ln(5)
        
        for i, article in enumerate(articles[:10], 1):  # 상위 10개만
            title = article.get('title', 'No Title')
            title = title[:80] + '...' if len(title) > 80 else title
            
            # 제목 안전 출력
            self.safe_text_output(f'{i}. {title}', font_size=11, is_bold=False)
            
            # 출처 정보 - 안전한 출력 사용
            source = article.get('source', 'Unknown')
            self.safe_text_output(f'   Source: {source}', font_size=10)
            
            # 감성 분석 결과 (있는 경우) - 안전한 출력 사용
            if 'sentiment' in article:
                sentiment = article['sentiment']['sentiment']
                score = article['sentiment']['score']
                self.safe_text_output(f'   Sentiment: {sentiment.upper()} (Score: {score})', font_size=10)
            
            # AI 요약 (있는 경우)
            if 'ai_summary' in article and article['ai_summary']:
                summary = article['ai_summary'][:150] + '...' if len(article['ai_summary']) > 150 else article['ai_summary']
                
                # 요약 안전 출력
                self.safe_text_output(f'   Summary: {summary}', font_size=10)
            
            self.pdf.ln(3)
    
    def add_chart_section(self, chart_path):
        """차트 섹션 추가"""
        if os.path.exists(chart_path):
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.cell(0, 10, 'Keyword Visualization', ln=True)
            self.pdf.ln(5)
            
            # 이미지 추가 (차트)
            self.pdf.image(chart_path, x=10, y=40, w=190)
    
    def generate_report(self, keyword, articles, keywords_data, sentiment_stats=None, output_filename=None):
        """전체 리포트 생성"""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"news_report_{keyword}_{timestamp}.pdf"
        
        # 리포트 섹션들 추가
        self.add_title(keyword, len(articles))
        
        # 통계 정보 준비
        statistics = {'total_articles': len(articles)}
        if sentiment_stats:
            statistics.update(sentiment_stats)
        
        self.add_summary_section(statistics)
        self.add_keywords_section(keywords_data)
        self.add_articles_section(articles)
        
        # 워드클라우드 이미지 추가 (있는 경우)
        wordcloud_path = "data/wordcloud_default.png"
        if os.path.exists(wordcloud_path):
            self.add_chart_section(wordcloud_path)
        
        # PDF 저장
        output_path = f"data/{output_filename}"
        try:
            self.pdf.output(output_path)
            return output_path
        except Exception as e:
            print(f"❌ PDF 생성 오류: {e}")
            return None
    
    def create_sentiment_chart(self, sentiment_stats, filename="sentiment_chart.png"):
        """감성 분석 차트 생성"""
        if not sentiment_stats or 'positive_count' not in sentiment_stats:
            return None
        
        try:
            # 파이 차트 생성
            labels = ['Positive', 'Negative', 'Neutral']
            sizes = [
                sentiment_stats['positive_count'],
                sentiment_stats['negative_count'],
                sentiment_stats['neutral_count']
            ]
            colors = ['#4CAF50', '#F44336', '#FFC107']
            
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Sentiment Analysis Results', fontsize=16, fontweight='bold')
            plt.axis('equal')
            
            chart_path = f"data/{filename}"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"❌ 감성 차트 생성 오류: {e}")
            return None

if __name__ == "__main__":
    # 개발용 테스트 코드
    pass