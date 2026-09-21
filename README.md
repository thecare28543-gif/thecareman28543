# The Careman Tool Dashboard

โปรเจกต์นี้เป็น Streamlit app และ deploy แบบ GitHub Pages ไม่ได้ เพราะต้องรัน Python

## Deploy ด้วย Streamlit Community Cloud (แนะนำ)

1. เปิด https://share.streamlit.io/
2. เข้าสู่ระบบด้วย GitHub
3. กด **Create app**
4. เลือก repository `thecare28543-gif/thecareman28543`
5. Branch: `main`
6. Main file path: `app/dashboard.py`
7. กด **Deploy**

Streamlit Cloud จะติดตั้ง package จาก `requirements.txt` ให้เอง

## Deploy ด้วย Render

1. เปิด https://dashboard.render.com/
2. เลือก **New > Blueprint**
3. เลือก repository นี้
4. Render จะอ่าน `render.yaml` และใช้คำสั่ง start ที่เตรียมไว้

## รันในเครื่อง

```bash
pip install -r requirements.txt
streamlit run app/dashboard.py
```

หมายเหตุ: ไฟล์ `index.html` เดิมมีเนื้อหา Python และอ้างถึงโมดูล `config`, `app.database`, `app.detector` และ `app.line_alert` ซึ่งยังไม่มีอยู่ใน repository เดิม จึงเตรียม `app/dashboard.py` แบบ demo ที่ deploy ได้ก่อน หากต้องการเปิดใช้ YOLOv8, SQLite และ LINE Alert จริง ต้องเพิ่มโมดูลเหล่านั้นและไฟล์ model/camera configuration ให้ครบ
