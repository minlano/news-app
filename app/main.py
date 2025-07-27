#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
키워드 뉴스 요약 및 분석 웹앱 메인 파일
Streamlit 기반 웹 대시보드
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
import atexit
import glob
from PIL import Image

# 상위 디렉토리의 모듈들을 import하기 위한 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from crawler.daum_crawler import DaumNewsCrawler
    from summarizer.text_summarizer import TextSummarizer
    from sentiment_analysis.sentiment import SentimentAnalyzer
    from report.report_generator import NewsReportGenerator
    from report.email_sender import EmailSender
    
    # keyword 모듈 충돌 방지를 위한 직접 import
    import importlib.util
    
    # keyword_extractor 직접 로드
    spec = importlib.util.spec_from_file_location("keyword_extractor", 
                                                  os.path.join(parent_dir, "keyword", "keyword_extractor.py"))
    keyword_extractor_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(keyword_extractor_module)
    KeywordExtractor = keyword_extractor_module.KeywordExtractor
    
    # wordcloud_gen 직접 로드
    spec = importlib.util.spec_from_file_location("wordcloud_gen", 
                                                  os.path.join(parent_dir, "keyword", "wordcloud_gen.py"))
    wordcloud_gen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wordcloud_gen_module)
    WordCloudGenerator = wordcloud_gen_module.WordCloudGenerator
    
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.stop()

def cleanup_temp_data():
    """임시 데이터 파일들 삭제"""
    try:
        # 삭제할 파일 패턴들
        temp_files = [
            'data/articles.json',
            'data/summarized_articles.json', 
            'data/keywords.json',
            'data/sentiment_analysis.json',
            'data/news_report_*.pdf',
            'data/sentiment_chart.png',
            'data/email_config.json',
            'data/wordcloud*.png'
        ]
        
        deleted_count = 0
        for pattern in temp_files:
            if '*' in pattern:
                # 와일드카드 패턴 처리
                for file_path in glob.glob(pattern):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_count += 1
            else:
                # 일반 파일 처리
                if os.path.exists(pattern):
                    os.remove(pattern)
                    deleted_count += 1
        
        if deleted_count > 0:
            print(f"🧹 임시 데이터 {deleted_count}개 파일 삭제 완료")
        
    except Exception as e:
        print(f"❌ 임시 데이터 삭제 중 오류: {e}")

def clear_search_results():
    """검색 결과 초기화"""
    try:
        # 삭제할 검색 결과 파일들
        search_files = [
            'data/articles.json',
            'data/summarized_articles.json', 
            'data/keywords.json',
            'data/sentiment_analysis.json',
            'data/wordcloud*.png'
        ]
        
        deleted_count = 0
        for pattern in search_files:
            if '*' in pattern:
                # 와일드카드 패턴 처리
                for file_path in glob.glob(pattern):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_count += 1
            else:
                # 일반 파일 처리
                if os.path.exists(pattern):
                    os.remove(pattern)
                    deleted_count += 1
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ 검색 결과 초기화 중 오류: {e}")
        return 0

# 프로그램 종료 시 임시 데이터 자동 삭제 등록
atexit.register(cleanup_temp_data)

def load_data():
    """저장된 데이터 파일들 로드"""
    data = {}
    
    # 기사 데이터 로드
    try:
        with open('data/articles.json', 'r', encoding='utf-8') as f:
            data['articles'] = json.load(f)
    except FileNotFoundError:
        data['articles'] = []
    
    # 요약된 기사 데이터 로드
    try:
        with open('data/summarized_articles.json', 'r', encoding='utf-8') as f:
            data['summarized_articles'] = json.load(f)
    except FileNotFoundError:
        data['summarized_articles'] = []
    
    # 키워드 데이터 로드
    try:
        with open('data/keywords.json', 'r', encoding='utf-8') as f:
            data['keywords'] = json.load(f)
    except FileNotFoundError:
        data['keywords'] = {'keywords': [], 'total_keywords': 0}
    
    return data

def run_full_pipeline(keyword, max_articles=10):
    """전체 파이프라인 실행"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1. 크롤링
        if max_articles >= 15:
            status_text.text(f"🔍 뉴스 크롤링 중... ({max_articles}개 기사, 2-3분 소요 예상)")
        else:
            status_text.text(f"🔍 뉴스 크롤링 중... ({max_articles}개 기사)")
        progress_bar.progress(10)
        
        crawler = DaumNewsCrawler()
        articles = crawler.search_news(keyword, max_articles)
        
        if not articles:
            st.error("❌ 크롤링된 기사가 없습니다.")
            return False
        
        status_text.text(f"📄 {len(articles)}개 기사 수집 완료! 본문 내용 추출 중...")
        progress_bar.progress(30)
        
        # 본문 수집
        for i, article in enumerate(articles):
            if i % 5 == 0:  # 5개마다 진행 상황 업데이트
                status_text.text(f"📖 본문 수집 중... ({i+1}/{len(articles)})")
            content = crawler.get_article_content(article['link'])
            article['content'] = content
        
        crawler.save_articles(articles)
        
        # 2. 요약
        status_text.text("📝 기사 요약 중...")
        progress_bar.progress(50)
        
        summarizer = TextSummarizer()
        summarized_articles = summarizer.summarize_articles(articles, method='simple')
        
        with open('data/summarized_articles.json', 'w', encoding='utf-8') as f:
            json.dump(summarized_articles, f, ensure_ascii=False, indent=2)
        
        # 3. 키워드 추출
        status_text.text("🔍 키워드 추출 및 분석 중...")
        progress_bar.progress(70)
        
        extractor = KeywordExtractor()
        keywords = extractor.extract_keywords_from_articles(articles, top_n=30)
        extractor.save_keywords(keywords)
        
        # 4. 감성 분석
        status_text.text("😊 감성 분석 중...")
        progress_bar.progress(75)
        
        analyzer = SentimentAnalyzer()
        analyzed_articles, sentiment_summary = analyzer.analyze_articles(articles)
        sentiment_stats = analyzer.get_sentiment_statistics(analyzed_articles)
        
        # 감성 분석 결과 저장
        analyzer.save_sentiment_analysis(analyzed_articles)
        
        # 5. 워드클라우드 생성
        status_text.text("☁️ 3가지 스타일 워드클라우드 생성 중...")
        progress_bar.progress(90)
        
        generator = WordCloudGenerator()
        generator.create_multiple_styles()
        
        progress_bar.progress(100)
        status_text.text(f"✅ 분석 완료! {len(articles)}개 기사, {len(keywords)}개 키워드, 감성분석 완료")
        
        return True
        
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
        return False

def display_articles(articles):
    """기사 목록 표시"""
    if not articles:
        st.info("📭 표시할 기사가 없습니다.")
        return
    
    for i, article in enumerate(articles, 1):
        with st.expander(f"📰 {i}. {article['title']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**출처:** {article.get('source', 'N/A')}")
                st.write(f"**링크:** {article.get('link', 'N/A')}")
                
                # AI 요약이 있으면 표시
                if article.get('ai_summary'):
                    st.write("**AI 요약:**")
                    st.write(article['ai_summary'])
                else:
                    st.write("**요약:**")
                    st.write(article.get('summary', 'N/A')[:200] + "...")
            
            with col2:
                link_url = article.get('link', '#')
                if link_url and link_url != '#':
                    st.markdown(f"[🔗 원문 보기]({link_url})")
                else:
                    st.write("링크 없음")

def display_keywords(keywords_data):
    """키워드 표시"""
    if not keywords_data or not keywords_data.get('keywords'):
        st.info("📭 표시할 키워드가 없습니다.")
        return
    
    keywords = keywords_data['keywords'][:15]  # 상위 15개 표시
    
    # 두 개 컬럼으로 나누기
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 키워드 순위")
        # 키워드 테이블
        df = pd.DataFrame(keywords)
        df.index = df.index + 1
        df.columns = ['키워드', '빈도']
        st.dataframe(df, use_container_width=True)
        
        # 키워드 클릭 검색 기능
        st.markdown("### 🔍 키워드로 새로 검색")
        st.markdown("아래 키워드를 클릭하면 해당 키워드로 새로 검색합니다:")
        
        # 키워드 버튼들을 3개씩 나누어 표시
        for i in range(0, min(12, len(keywords)), 3):
            button_cols = st.columns(3)
            for j, col in enumerate(button_cols):
                if i + j < len(keywords):
                    keyword_item = keywords[i + j]
                    keyword_word = keyword_item['word']
                    keyword_count = keyword_item['count']
                    
                    with col:
                        if st.button(f"🔍 {keyword_word} ({keyword_count})", key=f"search_{keyword_word}_{i}_{j}"):
                            # 세션 상태에 검색할 키워드 저장
                            st.session_state.search_keyword = keyword_word
                            st.experimental_rerun()
    
    with col2:
        st.subheader("📈 빈도 차트")
        # 키워드 빈도 차트
        chart_data = pd.DataFrame(keywords).set_index('word')['count']
        st.bar_chart(chart_data)

def main():
    """메인 웹앱 함수"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="📰 키워드 뉴스 요약 분석",
        page_icon="📰",
        layout="wide"
    )
    
    # 제목
    st.title("📰 키워드 뉴스 요약 및 분석 웹앱")
    st.markdown("---")
    
    # 세션 상태에서 검색할 키워드가 있는지 확인
    if 'search_keyword' in st.session_state:
        keyword_from_session = st.session_state.search_keyword
        del st.session_state.search_keyword  # 사용 후 삭제
    else:
        keyword_from_session = ""
    
    # 사이드바
    st.sidebar.header("🔍 검색 설정")
    keyword = st.sidebar.text_input("검색할 키워드를 입력하세요", 
                                   value=keyword_from_session, 
                                   placeholder="예: 부동산, 주식, 정치")
    max_articles = st.sidebar.slider("수집할 기사 수", 5, 20, 10)
    
    # 시간 경고문
    if max_articles >= 15:
        st.sidebar.warning("⏰ 15개 이상 수집 시 2-3분 정도 소요될 수 있습니다.")
    elif max_articles >= 10:
        st.sidebar.info("⏱️ 약 1-2분 정도 소요됩니다.")
    
    # 검색 버튼 또는 키워드 클릭으로 인한 자동 검색
    search_triggered = st.sidebar.button("🔍 뉴스 검색 및 분석") or keyword_from_session
    
    if search_triggered and keyword.strip():
        with st.spinner("분석 중..."):
            success = run_full_pipeline(keyword.strip(), max_articles)
            if success:
                st.success("✅ 분석 완료!")
                st.experimental_rerun()
    elif search_triggered and not keyword.strip():
        st.sidebar.error("키워드를 입력해주세요!")
    
    # 데이터 로드
    data = load_data()
    
    # 메인 컨텐츠
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["� 뉴스  기사", "🔍 키워드 분석", "☁️ 워드클라우드", "😊 감성 분석", "📊 PDF 리포트"])
    
    with tab1:
        st.header("📄 뉴스 기사 목록")
        
        # 요약된 기사가 있으면 우선 표시, 없으면 원본 기사 표시
        articles_to_show = data['summarized_articles'] if data['summarized_articles'] else data['articles']
        
        if articles_to_show:
            st.info(f"📊 총 {len(articles_to_show)}개 기사")
            display_articles(articles_to_show)
        else:
            # 사용방법 안내
            st.markdown("## 🚀 사용방법")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("""
                ### 📝 **1단계: 키워드 입력**
                - 왼쪽 사이드바에서 관심있는 키워드를 입력하세요
                - 예시: `부동산`, `주식`, `정치`, `경제`, `IT` 등
                
                ### 🔍 **2단계: 검색 실행**
                - 수집할 기사 수를 선택하세요 (5~20개)
                - "🔍 뉴스 검색 및 분석" 버튼을 클릭하세요
                """)
            
            with col2:
                st.markdown("""
                ### 📊 **3단계: 결과 확인**
                - **뉴스 기사**: 크롤링된 기사와 AI 요약
                - **키워드 분석**: 주요 키워드와 빈도 차트
                - **워드클라우드**: 3가지 스타일의 시각화
                - **감성 분석**: 긍정/부정/중립 감성 분류
                - **PDF 리포트**: 전체 분석 결과 리포트
                
                ### 💡 **추가 기능**
                - 워드클라우드 다운로드
                - PDF 리포트 이메일 발송
                - 키워드 클릭으로 재검색
                """)
            
            st.markdown("---")
            st.markdown("### 🎯 **주요 기능**")
            
            feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)
            
            with feature_col1:
                st.markdown("""
                **🔍 뉴스 크롤링**
                - 다음 뉴스에서 실시간 수집
                - 제목, 본문, 요약 자동 추출
                - 최대 20개 기사 수집 가능
                """)
            
            with feature_col2:
                st.markdown("""
                **📝 AI 요약**
                - 긴 기사를 간단하게 요약
                - 핵심 내용만 추출
                - 빠른 정보 파악 가능
                """)
            
            with feature_col3:
                st.markdown("""
                **😊 감성 분석**
                - 긍정/부정/중립 자동 분류
                - 키워드 기반 감성 점수
                - 전체 감성 동향 파악
                """)
            
            with feature_col4:
                st.markdown("""
                **📊 PDF 리포트**
                - 전체 분석 결과 통합
                - 이메일 자동 발송
                - 워드클라우드 포함
                """)
            
            st.info("👈 왼쪽 사이드바에서 키워드를 입력하고 시작해보세요!")
    
    with tab2:
        st.header("🔍 키워드 분석")
        
        if data['keywords']['keywords']:
            st.info(f"📊 총 {data['keywords']['total_keywords']}개 키워드 추출")
            display_keywords(data['keywords'])
        else:
            st.info("📭 아직 추출된 키워드가 없습니다.")
    
    with tab3:
        st.header("☁️ 키워드 워드클라우드")
        
        # 워드클라우드 스타일 선택 (3가지만)
        available_styles = []
        style_files = {
            'default': 'data/wordcloud_default.png',
            'dark': 'data/wordcloud_dark.png', 
            'rainbow': 'data/wordcloud_rainbow.png'
        }
        
        # 존재하는 파일들만 선택지에 추가
        for style, filepath in style_files.items():
            if os.path.exists(filepath):
                available_styles.append(style)
        
        if available_styles:
            selected_style = st.selectbox(
                "🎨 워드클라우드 스타일 선택:",
                available_styles,
                index=0
            )
            
            # 선택된 스타일의 워드클라우드 표시
            selected_path = style_files[selected_style]
            
            try:
                image = Image.open(selected_path)
                st.image(image, caption=f"{selected_style.title()} 스타일 워드클라우드", use_column_width=True)
                
                # 다운로드 버튼
                with open(selected_path, "rb") as file:
                    st.download_button(
                        label=f"📥 {selected_style} 스타일 다운로드",
                        data=file.read(),
                        file_name=f"wordcloud_{selected_style}.png",
                        mime="image/png"
                    )
                    
            except Exception as e:
                st.error(f"워드클라우드 이미지 로드 오류: {e}")
        else:
            st.info("📭 아직 생성된 워드클라우드가 없습니다.")
    
    with tab4:
        st.header("😊 감성 분석")
        
        # 감성 분석 데이터 로드
        try:
            with open('data/sentiment_analysis.json', 'r', encoding='utf-8') as f:
                sentiment_data = json.load(f)
            
            if sentiment_data and 'statistics' in sentiment_data:
                stats = sentiment_data['statistics']
                
                # 전체 감성 요약
                st.subheader("📊 전체 감성 분석 결과")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("😊 긍정적 기사", f"{stats['positive_count']}개", f"{stats['positive_ratio']}%")
                
                with col2:
                    st.metric("😞 부정적 기사", f"{stats['negative_count']}개", f"{stats['negative_ratio']}%")
                
                with col3:
                    st.metric("😐 중립적 기사", f"{stats['neutral_count']}개", f"{stats['neutral_ratio']}%")
                
                with col4:
                    overall_sentiment = stats['overall_sentiment']
                    sentiment_emoji = "😊" if overall_sentiment == "positive" else "😞" if overall_sentiment == "negative" else "😐"
                    st.metric("🎯 전체 감성", f"{sentiment_emoji} {overall_sentiment.upper()}", f"점수: {stats['average_score']}")
                
                # 감성 분포 차트
                st.subheader("📈 감성 분포")
                
                chart_data = pd.DataFrame({
                    '감성': ['긍정', '부정', '중립'],
                    '기사 수': [stats['positive_count'], stats['negative_count'], stats['neutral_count']]
                })
                
                st.bar_chart(chart_data.set_index('감성'))
                
                # 개별 기사 감성 분석 결과
                st.subheader("📰 개별 기사 감성 분석")
                
                if 'articles' in sentiment_data:
                    articles = sentiment_data['articles']
                    
                    for i, article in enumerate(articles[:10], 1):  # 상위 10개만 표시
                        sentiment = article['sentiment']
                        sentiment_type = sentiment['sentiment']
                        sentiment_score = sentiment['score']
                        
                        # 감성에 따른 색상 및 이모지
                        if sentiment_type == 'positive':
                            color = "🟢"
                            emoji = "😊"
                        elif sentiment_type == 'negative':
                            color = "🔴"
                            emoji = "😞"
                        else:
                            color = "🟡"
                            emoji = "😐"
                        
                        with st.expander(f"{color} {i}. {article['title'][:60]}... ({emoji} {sentiment_type.upper()})"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**감성:** {emoji} {sentiment_type.upper()}")
                                st.write(f"**감성 점수:** {sentiment_score}")
                                st.write(f"**긍정 키워드:** {sentiment['positive_count']}개")
                                st.write(f"**부정 키워드:** {sentiment['negative_count']}개")
                                
                                if article.get('ai_summary'):
                                    st.write("**요약:**")
                                    st.write(article['ai_summary'])
                            
                            with col2:
                                link_url = article.get('link', '#')
                                if link_url and link_url != '#':
                                    st.markdown(f"[🔗 원문 보기]({link_url})")
            else:
                st.info("📭 아직 감성 분석 결과가 없습니다.")
                
        except FileNotFoundError:
            st.info("📭 아직 감성 분석 결과가 없습니다.")
        except Exception as e:
            st.error(f"감성 분석 데이터 로드 오류: {e}")
    
    with tab5:
        st.header("📊 PDF 리포트 생성")
        
        # 리포트 생성 가능 여부 확인
        has_data = (os.path.exists('data/articles.json') and 
                   os.path.exists('data/keywords.json'))
        
        if has_data:
            st.subheader("📄 리포트 생성")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                **포함될 내용:**
                - 📊 분석 개요 및 통계
                - 📰 수집된 뉴스 기사 목록
                - 🔍 주요 키워드 분석
                - 😊 감성 분석 결과 (있는 경우)
                - ☁️ 워드클라우드 이미지
                """)
            
            with col2:
                if st.button("📄 PDF 리포트 생성", type="primary"):
                    with st.spinner("PDF 리포트 생성 중..."):
                        try:
                            # 데이터 로드
                            with open('data/articles.json', 'r', encoding='utf-8') as f:
                                articles = json.load(f)
                            
                            with open('data/keywords.json', 'r', encoding='utf-8') as f:
                                keywords_data = json.load(f)
                            
                            # 감성 분석 데이터 로드 (있는 경우)
                            sentiment_stats = None
                            try:
                                with open('data/sentiment_analysis.json', 'r', encoding='utf-8') as f:
                                    sentiment_data = json.load(f)
                                    sentiment_stats = sentiment_data.get('statistics')
                            except FileNotFoundError:
                                pass
                            
                            # PDF 리포트 생성
                            generator = NewsReportGenerator()
                            pdf_path = generator.generate_report(
                                keyword=keyword if keyword else "분석결과",
                                articles=articles,
                                keywords_data=keywords_data,
                                sentiment_stats=sentiment_stats
                            )
                            
                            if pdf_path:
                                st.success("✅ PDF 리포트가 생성되었습니다!")
                                
                                # 다운로드 버튼
                                with open(pdf_path, "rb") as pdf_file:
                                    st.download_button(
                                        label="📥 PDF 리포트 다운로드",
                                        data=pdf_file.read(),
                                        file_name=os.path.basename(pdf_path),
                                        mime="application/pdf"
                                    )
                            else:
                                st.error("❌ PDF 리포트 생성에 실패했습니다.")
                                
                        except Exception as e:
                            st.error(f"❌ 리포트 생성 중 오류: {e}")
            
            # 이메일 발송 기능
            st.subheader("📧 이메일 발송")
            
            # .env 파일 기반 간편 발송
            email_sender = EmailSender()
            env_config = email_sender.get_env_email_config()
            
            if env_config['gmail_email'] and env_config['gmail_password']:
                st.info(f"📧 발송자 이메일: {env_config['gmail_email']}")
                
                recipient_email = st.text_input(
                    "수신자 이메일",
                    placeholder="recipient@example.com"
                )
                
                if st.button("📧 간편 이메일 발송", type="primary"):
                    if recipient_email:
                        with st.spinner("이메일 발송 중..."):
                            try:
                                # 최신 PDF 파일 찾기
                                pdf_files = glob.glob("data/news_report_*.pdf")
                                if pdf_files:
                                    latest_pdf = max(pdf_files, key=os.path.getctime)
                                    
                                    # 감성 분석 통계 로드
                                    sentiment_stats = None
                                    try:
                                        with open('data/sentiment_analysis.json', 'r', encoding='utf-8') as f:
                                            sentiment_data = json.load(f)
                                            sentiment_stats = sentiment_data.get('statistics')
                                    except FileNotFoundError:
                                        pass
                                    
                                    # .env 기반 이메일 발송
                                    success, message = email_sender.send_report_email_with_env(
                                        recipient_email=recipient_email,
                                        keyword=keyword if keyword else "분석결과",
                                        article_count=len(data.get('articles', [])),
                                        pdf_path=latest_pdf,
                                        sentiment_stats=sentiment_stats
                                    )
                                    
                                    if success:
                                        st.success(f"✅ {message}")
                                    else:
                                        st.error(f"❌ {message}")
                                else:
                                    st.error("❌ 발송할 PDF 리포트가 없습니다. 먼저 리포트를 생성해주세요.")
                                    
                            except Exception as e:
                                st.error(f"❌ 이메일 발송 중 오류: {e}")
                    else:
                        st.error("❌ 수신자 이메일을 입력해주세요.")
            else:
                st.warning("⚠️ .env 파일에 GMAIL_EMAIL과 GMAIL_APP_PASSWORD를 설정해주세요.")
            

        else:
            st.info("📭 리포트를 생성하려면 먼저 뉴스 검색을 실행해주세요.")
    
    # 푸터
    st.markdown("---")
    st.markdown("🎉 **키워드 뉴스 요약 및 분석 웹앱**")
    st.markdown("📊 실시간 크롤링 | 📝 AI 요약 | 🔍 키워드 분석 | ☁️ 워드클라우드 시각화")
    
    # 기타 기능 버튼들
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔄 기타 기능**")
    
    # 데이터 새로고침 버튼
    if st.sidebar.button("🔄 데이터 새로고침", help="화면의 데이터를 최신 상태로 업데이트합니다"):
        st.experimental_rerun()
    
    # 검색 결과 초기화 버튼
    if st.sidebar.button("🗑️ 검색 결과 초기화", help="모든 검색 결과와 분석 데이터를 삭제합니다"):
        with st.spinner("검색 결과 초기화 중..."):
            deleted_count = clear_search_results()
            if deleted_count > 0:
                st.sidebar.success(f"✅ {deleted_count}개 파일 삭제 완료!")
                st.experimental_rerun()
            else:
                st.sidebar.info("📭 삭제할 검색 결과가 없습니다.")

if __name__ == "__main__":
    main()