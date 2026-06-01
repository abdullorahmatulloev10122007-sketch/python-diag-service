# ui/app.py
import streamlit as st
import requests
from datetime import datetime

# Принудительная очистка кэша
st.cache_resource.clear()
st.cache_data.clear()

API_URL = "http://127.0.0.1:8000/analyze/"

st.set_page_config(
    page_title="PyDiag Pro - Анализ Python кода",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# 🎨 Профессиональный CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Фон */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        background-attachment: fixed;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Карточки */
    .metric-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
    }
    
    .feature-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 15px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
    }
    
    /* Поле кода */
    .stTextArea textarea {
        background: #0b1120;
        color: #e2e8f0;
        border: 2px solid #1e293b;
        border-radius: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Заголовки */
    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
    }
    
    /* Метрики */
    [data-testid="stMetricValue"] {
        color: #3b82f6;
        font-size: 2.5rem;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Скрытие элементов */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Бейджи */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    .badge-error { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .badge-info { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .css-1r6slb0 {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# 🔄 Инициализация состояния
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# 📱 Sidebar навигация
with st.sidebar:
    st.markdown("### 🔍 PyDiag Pro")
    st.markdown("---")
    
    # Навигация
    if st.button("🏠 Главная", use_container_width=True, 
                 type="primary" if st.session_state.page == 'home' else "secondary"):
        st.session_state.page = 'home'
        st.rerun()
    
    if st.button("📊 Анализ кода", use_container_width=True,
                 type="primary" if st.session_state.page == 'analyze' else "secondary"):
        st.session_state.page = 'analyze'
        st.rerun()
    
    if st.button("📚 База знаний", use_container_width=True,
                 type="primary" if st.session_state.page == 'knowledge' else "secondary"):
        st.session_state.page = 'knowledge'
        st.rerun()
    
    if st.button("📈 Статистика", use_container_width=True,
                 type="primary" if st.session_state.page == 'stats' else "secondary"):
        st.session_state.page = 'stats'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ О приложении")
    st.info("**PyDiag Pro** — профессиональный инструмент для анализа Python-кода с использованием AST-парсинга.")
    
    st.markdown("---")
    st.markdown(f"*v2.0.0 | Build {datetime.now().strftime('%Y.%m')}*")

# 🏠 Главная страница
if st.session_state.page == 'home':
    st.markdown("### 👋 Добро пожаловать в PyDiag Pro")
    st.markdown("---")
    
    # Hero секция
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ## Интеллектуальный анализатор Python-кода
        
        **PyDiag Pro** помогает разработчикам писать чистый и эффективный код.
        Наш анализатор находит ошибки, уязвимости и нарушения стиля PEP 8.
        """)
        
        st.markdown("### ✨ Возможности")
        features = [
            ("🎯", "10+ типов проверок кода", "От синтаксических ошибок до стилистических нарушений"),
            ("⚡", "Мгновенный анализ", "Результат за доли секунды даже для больших файлов"),
            ("📖", "Подробные объяснения", "Каждая ошибка сопровождается ссылкой на документацию"),
            ("📊", "Оценка качества", "Объективная метрика от 0 до 100 баллов"),
        ]
        
        for icon, title, desc in features:
            st.markdown(f"""
            <div class="feature-card">
                <h4>{icon} {title}</h4>
                <p style="color: #94a3b8; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin-top: 0;">📊 Статистика</h3>
            <p style="color: #94a3b8; font-size: 14px;">За все время</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Подсчёт статистики
        total_checks = len(st.session_state.analysis_history)
        avg_score = "0/100"
        if total_checks > 0:
            scores = [h.get('score', 0) for h in st.session_state.analysis_history if isinstance(h.get('score'), (int, float))]
            if scores:
                avg_score = f"{sum(scores)/len(scores):.0f}/100"
        
        # Отображение метрик
        st.metric(label="Всего проверок", value=total_checks, delta=None)
        st.metric(label="Средний балл", value=avg_score, delta=None)
        
        st.markdown("---")
        st.markdown("### 🚀 Быстрый старт")
        if st.button("Начать анализ", use_container_width=True):
            st.session_state.page = 'analyze'
            st.rerun()

# 🔍 Страница анализа
elif st.session_state.page == 'analyze':
    st.markdown("### 🔍 Анализ кода")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code_input = st.text_area(
            "Вставьте ваш код",
            height=300,
            placeholder="# Пример кода для анализа\ndef calculate_sum(a, b):\n    return a + b\n\nresult = calculate_sum(5, 3)\nprint(result)",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("### Настройки")
        st.selectbox("Язык", ["Python 3.10", "Python 3.11", "Python 3.12"])
        st.checkbox("Строгий режим", value=True)
        st.checkbox("Показывать warnings", value=True)
        st.checkbox("Показывать info", value=False)
        
        st.markdown("---")
        if st.button("🔍 Анализировать", use_container_width=True, type="primary"):
            if not code_input.strip():
                st.error("⚠️ Введите код для анализа!")
            else:
                with st.spinner("⏳ Выполняется анализ..."):
                    try:
                        response = requests.post(API_URL, json={"code": code_input, "user_id": None}, timeout=30)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.analysis_history.append(result)
                            
                            # Результаты
                            st.markdown("---")
                            st.markdown("### 📊 Результаты анализа")
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Оценка качества", f"{result['score']}/100",
                                         delta="↑ Отлично" if result['score'] >= 80 else "↓ Нужно улучшить")
                            with col_b:
                                st.metric("Найдено ошибок", result['errors_count'])
                            with col_c:
                                level = "🔥 Отлично" if result['score'] >= 80 else "👍 Хорошо" if result['score'] >= 60 else "⚠️ Требует доработки"
                                st.metric("Уровень", level)
                            
                            st.progress(result['score'] / 100)
                            
                            if result['errors']:
                                st.markdown("---")
                                st.markdown(f"### 🔴 Найдено ошибок: {result['errors_count']}")
                                
                                for idx, err in enumerate(result['errors'], 1):
                                    severity = err.get('severity', 'error')
                                    badge_class = "badge-error" if severity == 'error' else "badge-warning" if severity == 'warning' else "badge-info"
                                    
                                    with st.expander(f"{'❌' if severity == 'error' else '⚠️'} {err.get('type', 'Ошибка')} (строка {err.get('line', '?')})"):
                                        st.markdown(f"**Тип ошибки:** <span class='badge {badge_class}'>{err.get('type')}</span>", unsafe_allow_html=True)
                                        st.markdown(f"**Строка:** `{err.get('line', 'N/A')}`")
                                        st.markdown(f"**Описание:** {err.get('message', '')}")
                                        st.markdown(f"**Как исправить:** {err.get('fix', '')}")
                                        st.markdown(f"**📖 [Документация]({err.get('resource', '#')})**")
                            else:
                                st.success("🎉 Поздравляем! Код чистый и соответствует стандартам!")
                                st.balloons()
                            
                            if result.get('recommendations'):
                                st.markdown("---")
                                st.markdown("### 💡 Рекомендации")
                                for rec in result['recommendations']:
                                    st.info(f"📚 {rec}")
                                    
                        else:
                            st.error(f"❌ Ошибка сервера: {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"❌ Ошибка: {str(e)}")
                        st.info("💡 Убедитесь, что backend запущен: `uvicorn app.main:app --reload`")

# 📚 База знаний
elif st.session_state.page == 'knowledge':
    st.markdown("### 📚 База знаний")
    st.markdown("---")
    
    st.markdown("### Типичные ошибки Python")
    
    errors_db = {
        "Переопределение builtins": {
            "desc": "Не используйте имена встроенных функций для переменных",
            "bad": "list = [1, 2, 3]",
            "good": "my_list = [1, 2, 3]",
            "link": "https://docs.python.org/3/library/functions.html"
        },
        "Сравнение с True/False": {
            "desc": "Используйте неявное приведение к bool",
            "bad": "if x == True:",
            "good": "if x:",
            "link": "https://realpython.com/python-boolean/"
        },
        "Изменяемые аргументы": {
            "desc": "Не используйте изменяемые объекты как аргументы по умолчанию",
            "bad": "def func(lst=[]):",
            "good": "def func(lst=None):",
            "link": "https://docs.python-guide.org/writing/gotchas/"
        }
    }
    
    for title, info in errors_db.items():
        with st.expander(f"📖 {title}"):
            st.write(info['desc'])
            st.markdown("**❌ Неправильно:**")
            st.code(info['bad'], language='python')
            st.markdown("**✅ Правильно:**")
            st.code(info['good'], language='python')
            st.markdown(f"[📖 Подробнее]({info['link']})")

# 📈 Статистика
elif st.session_state.page == 'stats':
    st.markdown("### 📈 Статистика")
    st.markdown("---")
    
    if st.session_state.analysis_history:
        col1, col2, col3 = st.columns(3)
        
        scores = [h.get('score', 0) for h in st.session_state.analysis_history]
        
        with col1:
            st.metric("Всего проверок", len(scores))
        with col2:
            st.metric("Средний балл", f"{sum(scores)/len(scores):.1f}/100")
        with col3:
            st.metric("Лучший результат", f"{max(scores)}/100")
        
        st.markdown("---")
        st.markdown("### История проверок")
        for idx, result in enumerate(reversed(st.session_state.analysis_history), 1):
            with st.expander(f"Проверка #{len(st.session_state.analysis_history) - idx + 1} - {result.get('score', 0)}/100"):
                st.write(f"Ошибок найдено: {result.get('errors_count', 0)}")
                st.write(f"Дата: {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.info("📊 Пока нет данных. Проведите первый анализ кода!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 20px; font-size: 13px;'>
    PyDiag Pro v2.0 | Python Code Diagnostics Service | Проект №86 | IT.Бирюлёво 2026
</div>
""", unsafe_allow_html=True)