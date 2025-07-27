#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
키워드 뉴스 요약 및 분석 웹앱 실행 파일
Streamlit 앱을 실행하는 진입점
"""

import subprocess
import sys
import os
import atexit
import glob

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

def main():
    """Streamlit 앱 실행"""
    # 프로그램 종료 시 임시 데이터 자동 삭제 등록
    atexit.register(cleanup_temp_data)
    
    try:
        # app/main.py 파일이 존재하는지 확인
        app_path = os.path.join("app", "main.py")
        if not os.path.exists(app_path):
            print(f"❌ {app_path} 파일을 찾을 수 없습니다.")
            return
        
        print("🚀 키워드 뉴스 요약 웹앱을 시작합니다...")
        print("📱 브라우저에서 http://localhost:8501 로 접속하세요")
        print("💡 앱 종료 시 모든 임시 데이터가 자동으로 삭제됩니다.")
        
        # Streamlit 앱 실행
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
        
    except KeyboardInterrupt:
        print("\n👋 앱을 종료합니다.")
        print("🧹 임시 데이터를 정리하는 중...")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()