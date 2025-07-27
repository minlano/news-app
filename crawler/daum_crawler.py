#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다음 뉴스 크롤러
키워드로 뉴스 검색하고 기사 내용을 수집
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os

class DaumNewsCrawler:
    def __init__(self):
        self.base_url = "https://search.daum.net/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_news(self, keyword, max_articles=10):
        """키워드로 뉴스 검색 (여러 페이지 지원)"""
        all_articles = []
        page = 1
        
        while len(all_articles) < max_articles and page <= 5:  # 최대 5페이지까지
            # 첫 번째 페이지와 나머지 페이지의 파라미터가 다름
            if page == 1:
                params = {
                    'w': 'news',
                    'nil_search': 'btn',
                    'DA': 'NTB',
                    'enc': 'utf8',
                    'cluster': 'y',
                    'cluster_page': '1',
                    'q': keyword
                }
            else:
                params = {
                    'w': 'news',
                    'nil_search': 'btn',
                    'DA': 'PGD',
                    'enc': 'utf8',
                    'cluster': 'y',
                    'cluster_page': '1',
                    'p': str(page),
                    'q': keyword
                }
            
            page_articles = self._search_single_page(params, max_articles - len(all_articles))
            
            if not page_articles:
                break
            
            all_articles.extend(page_articles)
            page += 1
            time.sleep(1)  # 페이지 간 요청 간격
        
        return all_articles[:max_articles]  # 요청한 개수만큼만 반환
    
    def _search_single_page(self, params, max_articles_for_page):
        """단일 페이지에서 뉴스 검색"""
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 다양한 뉴스 아이템 선택자 시도
            selectors = [
                'div.c-item-content',
                'div.wrap_cont',
                'li.news',
                'div.item-title',
                'div.news-item',
                'article'
            ]
            
            news_items = []
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    news_items = items[:max_articles_for_page]
                    break
            
            if not news_items:
                # 모든 링크 중에서 뉴스 관련 링크 찾기
                all_links = soup.find_all('a', href=True)
                news_links = [link for link in all_links if 'news' in link.get('href', '').lower()]
                
                for i, link in enumerate(news_links[:max_articles_for_page], 1):
                    title = link.get_text(strip=True)
                    if title and len(title) > 10:
                        article_data = {
                            'title': title,
                            'link': link.get('href'),
                            'summary': "",
                            'source': "다음뉴스",
                            'content': ""
                        }
                        articles.append(article_data)
                
                return articles
            
            # 정상적인 뉴스 아이템 처리
            for i, item in enumerate(news_items, 1):
                if len(articles) >= max_articles_for_page:
                    break
                    
                try:
                    # 제목 선택자 시도
                    title_elem = None
                    title_selectors = ['a.f_link_b', 'a.tit-g', 'a[class*="tit"]', 'a[class*="link"]']
                    
                    for selector in title_selectors:
                        title_elem = item.select_one(selector)
                        if title_elem and title_elem.get_text(strip=True) and len(title_elem.get_text(strip=True)) > 10:
                            break
                    
                    # 일반 a 태그 시도
                    if not title_elem:
                        all_links = item.find_all('a')
                        for link in all_links:
                            text = link.get_text(strip=True)
                            if text and len(text) > 15 and 'http' in link.get('href', ''):
                                title_elem = link
                                break
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 요약 텍스트 추출
                    summary_selectors = ['p.c-item-text', '.summary', '.desc', 'p']
                    summary = ""
                    for selector in summary_selectors:
                        summary_elem = item.select_one(selector)
                        if summary_elem:
                            summary = summary_elem.get_text(strip=True)
                            break
                    
                    # 언론사 정보
                    source_selectors = ['span.c-item-source', '.source', '.press']
                    source = "다음뉴스"
                    for selector in source_selectors:
                        source_elem = item.select_one(selector)
                        if source_elem:
                            source = source_elem.get_text(strip=True)
                            break
                    
                    if title and len(title) > 5:
                        article_data = {
                            'title': title,
                            'link': link,
                            'summary': summary,
                            'source': source,
                            'content': ""
                        }
                        
                        articles.append(article_data)
                        time.sleep(0.2)  # 서버 부하 방지
                    
                except Exception as e:
                    continue
            
            return articles
            
        except Exception as e:
            return []
    
    def get_article_content(self, article_url):
        """개별 기사의 본문 내용 추출"""
        try:
            response = requests.get(article_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 다양한 뉴스 사이트의 본문 선택자 시도
            content_selectors = [
                'div.article_view',
                'div#harmonyContainer',
                'div.news_end',
                'div.article-body',
                'div.article_body',
                'div.read_body'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            return content[:1000] if content else ""  # 1000자로 제한
            
        except Exception as e:
            print(f"❌ 본문 추출 오류: {e}")
            return ""
    
    def save_articles(self, articles, filename="articles.json"):
        """수집한 기사를 JSON 파일로 저장"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"💾 기사 데이터가 {filepath}에 저장되었습니다.")
            return filepath
        except Exception as e:
            print(f"❌ 파일 저장 오류: {e}")
            return None

if __name__ == "__main__":
    # 개발용 테스트 코드
    pass