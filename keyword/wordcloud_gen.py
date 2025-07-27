#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드클라우드 생성기
matplotlib과 wordcloud를 사용한 시각화
"""

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import os

class WordCloudGenerator:
    def __init__(self):
        self.font_path = self.get_korean_font()
        
    def get_korean_font(self):
        """한글 폰트 경로 찾기"""
        # Windows 시스템 폰트 경로들 (더 많은 옵션 추가)
        font_paths = [
            'C:/Windows/Fonts/malgun.ttf',      # 맑은 고딕
            'C:/Windows/Fonts/malgunbd.ttf',    # 맑은 고딕 Bold
            'C:/Windows/Fonts/gulim.ttc',       # 굴림
            'C:/Windows/Fonts/batang.ttc',      # 바탕
            'C:/Windows/Fonts/dotum.ttc',       # 돋움
            'C:/Windows/Fonts/NanumGothic.ttf', # 나눔고딕
            'C:/Windows/Fonts/H2GTRM.TTF',      # 한컴 바탕
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        
        # matplotlib 한글 폰트 설정 시도
        try:
            import matplotlib.font_manager as fm
            font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
            korean_fonts = [f for f in font_list if any(name in f.lower() for name in ['malgun', 'gulim', 'batang', 'dotum', 'nanum'])]
            
            if korean_fonts:
                return korean_fonts[0]
        except:
            pass
        
        return None
    
    def create_wordcloud(self, keywords, width=800, height=400, max_words=50, style='default'):
        """워드클라우드 생성"""
        try:
            # 키워드가 리스트 형태인 경우 딕셔너리로 변환
            if isinstance(keywords, list):
                word_freq = {word: count for word, count in keywords}
            else:
                word_freq = keywords
            
            if not word_freq:
                print("❌ 키워드가 없습니다.")
                return None
            
            print(f"☁️ {style} 스타일 워드클라우드 생성 중... ({len(word_freq)}개 키워드)")
            
            # 스타일별 설정 (3가지만 유지)
            style_configs = {
                'default': {
                    'background_color': 'white',
                    'colormap': 'viridis',
                    'prefer_horizontal': 0.7,
                },
                'dark': {
                    'background_color': 'black',
                    'colormap': 'plasma',
                    'prefer_horizontal': 0.6,
                },
                'rainbow': {
                    'background_color': 'white',
                    'colormap': 'rainbow',
                    'prefer_horizontal': 0.5,
                }
            }
            
            # 선택된 스타일 설정 가져오기
            style_config = style_configs.get(style, style_configs['default'])
            
            # 기본 워드클라우드 설정
            wordcloud_config = {
                'width': width,
                'height': height,
                'max_words': max_words,
                'relative_scaling': 0.5,
                'min_font_size': 12,
                'max_font_size': 80,
                'random_state': 42,  # 일관된 결과를 위해
                'collocations': False,  # 단어 조합 방지
            }
            
            # 스타일 설정 추가
            wordcloud_config.update(style_config)
            
            # 한글 폰트가 있으면 추가
            if self.font_path:
                wordcloud_config['font_path'] = self.font_path
            
            # 워드클라우드 생성
            wordcloud = WordCloud(**wordcloud_config).generate_from_frequencies(word_freq)
            
            return wordcloud
            
        except Exception as e:
            print(f"❌ 워드클라우드 생성 오류: {e}")
            return None
    
    def save_wordcloud(self, wordcloud, filename="wordcloud.png", dpi=300):
        """워드클라우드를 이미지 파일로 저장"""
        try:
            if not wordcloud:
                print("❌ 워드클라우드가 없습니다.")
                return None
            
            # data 폴더에 저장
            filepath = f"data/{filename}"
            
            # matplotlib으로 저장 (제목 없이)
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            # 제목 제거하여 한글 폰트 문제 완전 해결
            plt.tight_layout()
            
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"💾 워드클라우드가 {filepath}에 저장되었습니다.")
            return filepath
            
        except Exception as e:
            print(f"❌ 워드클라우드 저장 오류: {e}")
            return None
    
    def display_wordcloud(self, wordcloud):
        """워드클라우드 화면에 표시"""
        try:
            if not wordcloud:
                print("❌ 워드클라우드가 없습니다.")
                return
            
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('뉴스 키워드 워드클라우드', fontsize=16, pad=20)
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"❌ 워드클라우드 표시 오류: {e}")
    
    def create_from_keywords_file(self, keywords_file="data/keywords.json", 
                                 output_file="wordcloud.png", style='default'):
        """키워드 파일에서 워드클라우드 생성"""
        try:
            # 키워드 파일 로드
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keyword_data = json.load(f)
            
            # 키워드 딕셔너리 생성
            keywords = keyword_data.get('keywords', [])
            word_freq = {item['word']: item['count'] for item in keywords}
            
            # 워드클라우드 생성
            wordcloud = self.create_wordcloud(word_freq, style=style)
            
            if wordcloud:
                # 저장
                self.save_wordcloud(wordcloud, output_file)
                return wordcloud
            
            return None
            
        except FileNotFoundError:
            print(f"❌ {keywords_file} 파일을 찾을 수 없습니다.")
            return None
        except Exception as e:
            print(f"❌ 워드클라우드 생성 오류: {e}")
            return None
    
    def create_multiple_styles(self, keywords_file="data/keywords.json"):
        """3가지 스타일의 워드클라우드 생성 (속도 최적화)"""
        styles = ['default', 'dark', 'rainbow']
        
        print("🎨 3가지 스타일의 워드클라우드 생성 중...")
        
        for style in styles:
            output_file = f"wordcloud_{style}.png"
            print(f"📸 {style} 스타일 생성 중...")
            
            wordcloud = self.create_from_keywords_file(
                keywords_file=keywords_file,
                output_file=output_file,
                style=style
            )
            
            if wordcloud:
                print(f"✅ {style} 스타일 완료: data/{output_file}")
            else:
                print(f"❌ {style} 스타일 실패")
        
        print("🎉 3가지 스타일 워드클라우드 생성 완료!")

if __name__ == "__main__":
    # 개발용 테스트 코드
    pass