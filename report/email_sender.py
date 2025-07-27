#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이메일 자동 발송 모듈
PDF 리포트를 이메일로 전송
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from datetime import datetime
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class EmailSender:
    def __init__(self):
        # 주요 이메일 서비스 SMTP 설정
        self.smtp_configs = {
            'gmail': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True
            },
            'naver': {
                'server': 'smtp.naver.com',
                'port': 587,
                'use_tls': True
            },
            'daum': {
                'server': 'smtp.daum.net',
                'port': 587,
                'use_tls': True
            },
            'outlook': {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True
            }
        }
    
    def detect_email_provider(self, email):
        """이메일 주소에서 서비스 제공자 감지"""
        if '@gmail.com' in email:
            return 'gmail'
        elif '@naver.com' in email:
            return 'naver'
        elif '@daum.net' in email or '@hanmail.net' in email:
            return 'daum'
        elif '@outlook.com' in email or '@hotmail.com' in email:
            return 'outlook'
        else:
            return 'gmail'  # 기본값
    
    def create_email_content(self, keyword, article_count, sentiment_stats=None):
        """이메일 본문 생성"""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    📰 뉴스 분석 리포트
                </h2>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #495057; margin-top: 0;">분석 개요</h3>
                    <ul style="list-style-type: none; padding: 0;">
                        <li><strong>🔍 검색 키워드:</strong> {keyword}</li>
                        <li><strong>📊 분석 기사 수:</strong> {article_count}개</li>
                        <li><strong>📅 분석 일시:</strong> {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")}</li>
                    </ul>
                </div>
        """
        
        # 감성 분석 결과 추가 (있는 경우)
        if sentiment_stats and 'positive_count' in sentiment_stats:
            html_content += f"""
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">📈 감성 분석 결과</h3>
                    <ul style="list-style-type: none; padding: 0;">
                        <li><strong>😊 긍정적 기사:</strong> {sentiment_stats['positive_count']}개 ({sentiment_stats['positive_ratio']}%)</li>
                        <li><strong>😞 부정적 기사:</strong> {sentiment_stats['negative_count']}개 ({sentiment_stats['negative_ratio']}%)</li>
                        <li><strong>😐 중립적 기사:</strong> {sentiment_stats['neutral_count']}개 ({sentiment_stats['neutral_ratio']}%)</li>
                        <li><strong>🎯 전체 감성:</strong> <span style="color: {'#28a745' if sentiment_stats['overall_sentiment'] == 'positive' else '#dc3545' if sentiment_stats['overall_sentiment'] == 'negative' else '#6c757d'}; font-weight: bold;">{sentiment_stats['overall_sentiment'].upper()}</span></li>
                    </ul>
                </div>
            """
        
        html_content += """
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #856404; margin-top: 0;">📎 첨부 파일</h3>
                    <p>상세한 분석 결과는 첨부된 PDF 리포트를 확인해주세요.</p>
                    <ul>
                        <li>📄 뉴스 분석 리포트 (PDF)</li>
                        <li>☁️ 키워드 워드클라우드 이미지</li>
                        <li>📊 상세 분석 데이터</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 14px;">
                        이 리포트는 키워드 뉴스 분석 시스템에서 자동 생성되었습니다.<br>
                        📧 자동 발송 시스템 | 🤖 AI 기반 분석
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_report_email(self, sender_email, sender_password, recipient_email, 
                         keyword, article_count, pdf_path, sentiment_stats=None):
        """리포트 이메일 발송"""
        try:
            # 이메일 서비스 제공자 감지
            provider = self.detect_email_provider(sender_email)
            smtp_config = self.smtp_configs[provider]
            
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"📰 뉴스 분석 리포트 - {keyword} ({datetime.now().strftime('%Y.%m.%d')})"
            
            # HTML 본문 추가
            html_content = self.create_email_content(keyword, article_count, sentiment_stats)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # PDF 첨부파일 추가 (MIMEApplication 사용)
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    filename = os.path.basename(pdf_path)
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition', 
                        'attachment', 
                        filename=filename
                    )
                    msg.attach(pdf_attachment)
                    print(f"✅ PDF 첨부 완료: {filename}")
            
            # 워드클라우드 이미지 첨부 (MIMEApplication 사용)
            wordcloud_path = "data/wordcloud_default.png"
            if os.path.exists(wordcloud_path):
                with open(wordcloud_path, "rb") as f:
                    image_filename = f"wordcloud_{keyword}.png"
                    image_attachment = MIMEApplication(f.read(), _subtype='png')
                    image_attachment.add_header(
                        'Content-Disposition', 
                        'attachment', 
                        filename=image_filename
                    )
                    msg.attach(image_attachment)
                    print(f"✅ 워드클라우드 이미지 첨부 완료: {image_filename}")
            
            # SMTP 서버 연결 및 이메일 발송
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            
            if smtp_config['use_tls']:
                server.starttls()
            
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            return True, "이메일이 성공적으로 발송되었습니다."
            
        except smtplib.SMTPAuthenticationError:
            return False, "이메일 인증에 실패했습니다. 이메일과 비밀번호를 확인해주세요."
        except smtplib.SMTPRecipientsRefused:
            return False, "수신자 이메일 주소가 올바르지 않습니다."
        except Exception as e:
            return False, f"이메일 발송 중 오류가 발생했습니다: {str(e)}"
    
    def save_email_config(self, sender_email, recipient_email):
        """이메일 설정 저장 (비밀번호 제외)"""
        try:
            config = {
                'sender_email': sender_email,
                'recipient_email': recipient_email,
                'last_updated': datetime.now().isoformat()
            }
            
            with open('data/email_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ 이메일 설정 저장 오류: {e}")
            return False
    
    def load_email_config(self):
        """저장된 이메일 설정 로드"""
        try:
            with open('data/email_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"❌ 이메일 설정 로드 오류: {e}")
            return {}
    
    def get_env_email_config(self):
        """환경 변수에서 이메일 설정 로드"""
        return {
            'gmail_email': os.getenv('GMAIL_EMAIL', '').strip("'\""),
            'gmail_password': os.getenv('GMAIL_APP_PASSWORD', '').strip("'\"")
        }
    
    def send_report_email_with_env(self, recipient_email, keyword, article_count, pdf_path, sentiment_stats=None):
        """환경 변수를 사용한 이메일 발송"""
        env_config = self.get_env_email_config()
        
        if not env_config['gmail_email'] or not env_config['gmail_password']:
            return False, ".env 파일에 GMAIL_EMAIL과 GMAIL_APP_PASSWORD가 설정되지 않았습니다."
        
        return self.send_report_email(
            sender_email=env_config['gmail_email'],
            sender_password=env_config['gmail_password'],
            recipient_email=recipient_email,
            keyword=keyword,
            article_count=article_count,
            pdf_path=pdf_path,
            sentiment_stats=sentiment_stats
        )

if __name__ == "__main__":
    # 개발용 테스트 코드
    pass