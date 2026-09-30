python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('키 설정됨' if os.getenv('ANTHROPIC_API_KEY') else '키 없음 - .env 확인')"
