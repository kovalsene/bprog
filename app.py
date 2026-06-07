import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Редактор программы кружка", layout="wide")
st.title("📝 Заполнение программы обучения")

# === ИНИЦИАЛИЗАЦИЯ СЕССИИ ===
if 'df_current' not in st.session_state:
    st.session_state.df_current = None
if 'file_loaded' not in st.session_state:
    st.session_state.file_loaded = False
if 'original_filename' not in st.session_state:
    st.session_state.original_filename = None

# === ФУНКЦИИ ===
def load_excel_from_bytes(file_bytes):
    """Загружает Excel из байтов и возвращает DataFrame"""
    try:
        df = pd.read_excel(BytesIO(file_bytes))
        df = df.fillna('')
        return df
    except Exception as e:
        st.error(f"❌ Ошибка при чтении файла: {e}")
        return None

def save_to_bytes(df):
    """Сохраняет DataFrame в байты для скачивания"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Данные')
    return output.getvalue()

# === ЗАГРУЗКА ФАЙЛА ===
st.header("📂 Загрузка файла Excel")

uploaded_file = st.file_uploader(
    "Выберите файл Excel с данными кружка",
    type=['xlsx'],
    key="file_uploader",
    help="Загрузите Excel-файл, полученный от администратора"
)

# Обработка загрузки нового файла
if uploaded_file is not None:
    # Проверяем, новый ли это файл
    is_new = (st.session_state.original_filename != uploaded_file.name)
    
    if is_new or not st.session_state.file_loaded:
        df = load_excel_from_bytes(uploaded_file.getvalue())
        if df is not None:
            st.session_state.df_current = df
            st.session_state.file_loaded = True
            st.session_state.original_filename = uploaded_file.name
            st.success(f"✅ Файл **'{uploaded_file.name}'** успешно загружен!")

# Если файл не загружен
if not st.session_state.file_loaded:
    st.info("""
    ### 📋 Как работать с программой:
    
    1. **Загрузите файл** — нажмите "Upload" и выберите Excel-файл, который получили от педагога-организатора
    2. **Заполните данные** — все поля, кроме данных по заявке
    3. **Сохраните** — нажмите "Сохранить" и скачайте обновлённый файл
    4. **Продолжите позже** — загрузите сохранённый файл снова
    5. **Отправить** — готовый файл отправить на почту a.koval@ok654.ru 
    
    > 💡 Первые 10 полей защищены от изменений.
    """)
    st.stop()

# === ОСНОВНАЯ РАБОЧАЯ ОБЛАСТЬ ===
if st.session_state.file_loaded and st.session_state.df_current is not None:
    df = st.session_state.df_current.copy()
    
    # Информация о файле
    col_info1, col_info2 = st.columns([3, 1])
    with col_info1:
        st.success(f"📁 Работаем с файлом: **{st.session_state.original_filename}**")
    with col_info2:
        if st.button("🔄 Загрузить другой файл", use_container_width=True):
            st.session_state.file_loaded = False
            st.session_state.df_current = None
            st.session_state.original_filename = None
            st.rerun()
    
    all_columns = df.columns.tolist()
    
    # Получаем текущие значения
    current_values = {}
    if not df.empty:
        for col in all_columns:
            val = df.iloc[0][col]
            if pd.isna(val) or str(val).strip() in ['', 'nan']:
                current_values[col] = ''
            else:
                current_values[col] = str(val).strip()
    
    # === БЛОК 1: ТОЛЬКО ЧТЕНИЕ ===
    st.header("📋 Данные из заявки")
    st.caption("Эти поля заполнены администратором и не редактируются")
    
    readonly_cols = all_columns[:10]
    cols = st.columns(2)
    for i, col_name in enumerate(readonly_cols):
        with cols[i % 2]:
            st.text_input(
                f"**{col_name}**",
                value=current_values.get(col_name, ''),
                disabled=True,
                key=f"ro_{i}"
            )
    
    st.divider()
    
    # === БЛОК 2: ПОЯСНИТЕЛЬНАЯ ЗАПИСКА ===
    st.header("✍️ Пояснительная записка")
    st.info("⚠️ Не используйте название кружка, пишите просто: 'программа'")
    
    field_napravleno = all_columns[10] if len(all_columns) > 10 else None
    field_aktualnost = all_columns[11] if len(all_columns) > 11 else None
    field_cel = all_columns[12] if len(all_columns) > 12 else None
    field_results = all_columns[23] if len(all_columns) > 23 else None
    
    napravleno = st.text_area(
        "Продолжите фразу 'Программа направлена на...'",
        value=current_values.get(field_napravleno, '') if field_napravleno else '',
        height=100, key="napravleno"
    ) if field_napravleno else ""
    
    aktualnost = st.text_area(
        "Актуальность программы (современность, значимость, педагогическая целесообразность, отличительные особенности и т.п.)",
        value=current_values.get(field_aktualnost, '') if field_aktualnost else '',
        height=200, key="aktualnost"
    ) if field_aktualnost else ""
    
    cel = st.text_area(
        "Цель программы",
        value=current_values.get(field_cel, '') if field_cel else '',
        height=100, key="cel"
    ) if field_cel else ""
    
    results = st.text_area(
        "Планируемые результаты (совокупность знаний, умений, навыков, личностных качеств и компетенций, которые учащийся сможет демонстрировать по завершению освоения программы)",
        value=current_values.get(field_results, '') if field_results else '',
        height=150, key="results"
    ) if field_results else ""
    
    # === ЗАДАЧИ ===
    st.subheader("📌 Задачи программы")
    
    task_start_idx = 13
    task_end_idx = 22
    task_cols = all_columns[task_start_idx:task_end_idx+1] if len(all_columns) > task_end_idx else []
    
    filled_tasks = sum(1 for col in task_cols if current_values.get(col, ''))
    
    num_tasks = st.slider(
        "Количество задач (установите необходимое количество):", min_value=0, max_value=10,
        value=max(2, min(10, filled_tasks)) if filled_tasks > 0 else 3,
        step=1, key="num_tasks"
    )
    
    tasks = []
    if num_tasks > 0:
        for i in range(num_tasks):
            if i < len(task_cols):
                tasks.append(st.text_input(
                    f"Задача {i+1}",
                    value=current_values.get(task_cols[i], ''),
                    key=f"task_{i}"
                ))
            else:
                tasks.append(st.text_input(f"Задача {i+1}", value='', key=f"task_{i}"))
    
    st.divider()
    
    # === БЛОК 3: УЧЕБНЫЙ ПЛАН ===
    st.header("📅 Учебно-тематический план")
    
    hours_limit_col = all_columns[5] if len(all_columns) > 5 else None
    hours_limit = 36
    if hours_limit_col:
        try:
            hours_limit = int(float(current_values.get(hours_limit_col, '36')))
        except:
            hours_limit = 36
    
    st.info(f"⚠️ Лимит часов по программе: **{hours_limit}**. Не превышайте это значение.")
    st.info("УТП содержит перечень разделов (модулей) и тем, определяет их последовательность, количество часов по каждому разделу (модулю) и теме с указанием теоретических и практических занятий, а также форм аттестации и контроля. Количество часов в УТП указывается из расчёта на одну группу.")
    st.info("В колонке «Формы аттестации (контроля)» указываются формы подведения итогов освоения каждого раздела (зачеты, проекты, конкурсы, выставки и т.п.) и средства контроля (тесты, творческие задания и т.п.), если они применяются.")
    
    theme_start_idx = 24
    max_themes = 100
    
    table_data = []
    for i in range(max_themes):
        idx = theme_start_idx + i * 4
        if idx + 3 < len(all_columns):
            tema = current_values.get(all_columns[idx], '')
            teoria_raw = current_values.get(all_columns[idx + 1], '0')
            praktika_raw = current_values.get(all_columns[idx + 2], '0')
            kontrol = current_values.get(all_columns[idx + 3], '')
            
            try:
                teoria = float(teoria_raw) if teoria_raw and teoria_raw != '' else 0.0
            except:
                teoria = 0.0
            try:
                praktika = float(praktika_raw) if praktika_raw and praktika_raw != '' else 0.0
            except:
                praktika = 0.0
            
            table_data.append({
                'Номер': i + 1, 'Тема': tema,
                'Теория (часы)': teoria, 'Практика (часы)': praktika,
                'Форма контроля': kontrol,
            })
    
    filled_themes = sum(1 for r in table_data if r['Тема'] or r['Теория (часы)'] > 0 or r['Практика (часы)'] > 0)
    suggested_rows = max(filled_themes, 5)
    num_rows = st.number_input(
        "Количество тем для заполнения (установите необходимое количество):", min_value=0, max_value=len(table_data),
        value=min(suggested_rows, len(table_data)), step=1, key="num_themes"
    )
    num_rows = int(num_rows)
    
    if num_rows > 0:
        display_data = pd.DataFrame(table_data[:num_rows])
        edited_df = st.data_editor(
            display_data,
            column_config={
                'Номер': st.column_config.NumberColumn("№", disabled=True, width="small"),
                'Тема': st.column_config.TextColumn("Наименование раздела, темы", width="large"),
                'Теория (часы)': st.column_config.NumberColumn("Теория, часов", min_value=0, max_value=99, format="%g", width="small"),
                'Практика (часы)': st.column_config.NumberColumn("Практика, часов", min_value=0, max_value=99, format="%g", width="small"),
                'Форма контроля': st.column_config.TextColumn("Формы аттестации (контроля)", width="large"),
            },
            num_rows="fixed", use_container_width=True,
            key="theme_editor", hide_index=True,
        )
        
        total_teoria = edited_df['Теория (часы)'].sum()
        total_praktika = edited_df['Практика (часы)'].sum()
        total_hours = total_teoria + total_praktika
        
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric("📘 Теория", f"{total_teoria:.0f}")
        col_t2.metric("📗 Практика", f"{total_praktika:.0f}")
        col_t3.metric("📊 Всего", f"{total_hours:.0f}", 
                     delta=f"⚠️ +{total_hours - hours_limit:.0f}" if total_hours > hours_limit else None)
        col_t4.metric("🎯 Лимит", str(hours_limit))
        
        if total_hours > hours_limit:
            st.error(f"❌ Превышение на {total_hours - hours_limit:.0f} часов!")
    else:
        edited_df = pd.DataFrame(columns=['Номер', 'Тема', 'Теория (часы)', 'Практика (часы)', 'Форма контроля'])
    
    st.divider()
    
    # === СОДЕРЖАНИЕ ===
    st.header("📖 Содержание учебного плана")
    st.info("Реферативное (краткое) описание разделов (модулей) и тем программы в соответствии с учебным (тематическим) планом. В данном подразделе кратко описываются виды деятельности на занятии: теория (лекция, семинар, дискуссия, круглый стол, консультация и т.п.) и практика (практическая работа, лабораторная работа, самостоятельная работа, соревнование, игра, экскурсия и т.п.).")
    
    content_start_idx = theme_start_idx + max_themes * 4
    content_list = []
    if num_rows > 0:
        for i in range(num_rows):
            tema_name = edited_df.iloc[i]['Тема'] if i < len(edited_df) and edited_df.iloc[i]['Тема'] else f"Тема {i+1}"
            
            s_teoria_col = all_columns[content_start_idx + i*2] if content_start_idx + i*2 < len(all_columns) else None
            s_praktika_col = all_columns[content_start_idx + i*2 + 1] if content_start_idx + i*2 + 1 < len(all_columns) else None
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                s_teoria = st.text_area(f"📘 {tema_name} — Содержание теории",
                    value=current_values.get(s_teoria_col, '') if s_teoria_col else '',
                    height=80, key=f"ct_{i}")
            with col_s2:
                s_praktika = st.text_area(f"📗 {tema_name} — Содержание практики",
                    value=current_values.get(s_praktika_col, '') if s_praktika_col else '',
                    height=80, key=f"cp_{i}")
            
            content_list.append({'teoria': s_teoria, 'praktika': s_praktika})
    
    st.divider()
    
    # === ДОПОЛНИТЕЛЬНЫЕ СВЕДЕНИЯ ===
    st.header("📋 Дополнительные сведения")
    
    forms_col = all_columns[-3] if len(all_columns) >= 3 else None
    uslovia_col = all_columns[-2] if len(all_columns) >= 2 else None
    literatura_col = all_columns[-1] if len(all_columns) >= 1 else None
    
    st.info("Формы контроля и оценочные материалы")
    formy_kontrolya = st.text_area(
        "Данный структурный элемент Программы содержит описание форм подведения итогов реализации Программы текущего, промежуточного и итогового контроля (при наличии), которые перечисляются согласно учебному (тематическому) плану (зачеты, проекты, конкурсы, концерты, выставки, фестивали и т.п.) и описание средств контроля (тесты, творческие задания и т.п.), которые позволяют определить достижение планируемых результатов учащимися.",
        value=current_values.get(forms_col, '') if forms_col else '',
        height=150, key="forms"
    )
    
    st.info("Материально-технические условия реализации программы")
    uslovia = st.text_area(
        "Характеристики помещений, перечень оборудования, приборов и необходимых технических средств обучения, используемых в образовательном процессе.",
        value=current_values.get(uslovia_col, '') if uslovia_col else '',
        height=150, key="uslovia"
    )
    
    st.info("Учебно-методическое и информационное обеспечение программы")
    literatura = st.text_area(
        "Обеспеченность Программы методическими материалами и современными литературными источниками, поддерживающими процесс обучения (нормативно-правовые акты и документы; основная и дополнительная литература; Интернет-ресурсы). Все списки литературы и Интернет-ресурсов оформляются в соответствии с требованиями ГОСТ Р 7.0.100–2018.",
        value=current_values.get(literatura_col, '') if literatura_col else '',
        height=200, key="literatura"
    )
    
    st.divider()
    
    # === СОХРАНЕНИЕ И СКАЧИВАНИЕ ===
    st.header("💾 Сохранение и скачивание")
    
    if st.button("💾 СОХРАНИТЬ И СКАЧАТЬ ФАЙЛ", type="primary", use_container_width=True):
        new_values = current_values.copy()
        
        if field_napravleno: new_values[field_napravleno] = napravleno
        if field_aktualnost: new_values[field_aktualnost] = aktualnost
        if field_cel: new_values[field_cel] = cel
        if field_results: new_values[field_results] = results
        
        for i in range(10):
            if i < len(task_cols):
                new_values[task_cols[i]] = tasks[i] if i < len(tasks) else ''
        
        for i in range(max_themes):
            idx = theme_start_idx + i*4
            if idx + 3 < len(all_columns):
                if i < len(edited_df):
                    row = edited_df.iloc[i]
                    new_values[all_columns[idx]] = str(row['Тема']) if row['Тема'] else ''
                    new_values[all_columns[idx+1]] = str(int(row['Теория (часы)'])) if row['Теория (часы)'] > 0 else ''
                    new_values[all_columns[idx+2]] = str(int(row['Практика (часы)'])) if row['Практика (часы)'] > 0 else ''
                    new_values[all_columns[idx+3]] = str(row['Форма контроля']) if row['Форма контроля'] else ''
                else:
                    for j in range(4):
                        new_values[all_columns[idx+j]] = ''
        
        for i in range(max_themes):
            s_idx = content_start_idx + i*2
            if s_idx + 1 < len(all_columns):
                if i < len(content_list):
                    new_values[all_columns[s_idx]] = content_list[i]['teoria']
                    new_values[all_columns[s_idx+1]] = content_list[i]['praktika']
                else:
                    new_values[all_columns[s_idx]] = ''
                    new_values[all_columns[s_idx+1]] = ''
        
        if forms_col: new_values[forms_col] = formy_kontrolya
        if uslovia_col: new_values[uslovia_col] = uslovia
        if literatura_col: new_values[literatura_col] = literatura
        
        new_row = [new_values.get(col, '') for col in all_columns]
        df_new = pd.DataFrame([new_row], columns=all_columns)
        
        # Сохраняем в BytesIO
        excel_bytes = save_to_bytes(df_new)
        
        # Формируем имя файла для скачивания
        original_name = st.session_state.original_filename or "Программа.xlsx"
        download_name = f"Заполнено_{original_name}"
        
        st.success("✅ Данные подготовлены! Нажмите кнопку ниже для скачивания.")
        st.balloons()
        
        # Кнопка скачивания
        st.download_button(
            label="📥 СКАЧАТЬ ЗАПОЛНЕННЫЙ ФАЙЛ",
            data=excel_bytes,
            file_name=download_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button",
            use_container_width=True
        )
        
        st.info("💡 **Важно:** Сохраните скачанный файл. Чтобы продолжить редактирование позже, загрузите этот файл снова.")
