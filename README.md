# ระบบจัดการข้อมูลการเงิน

codex/create-web-app-with-login-and-data-export-ruoc1c
เว็บแอปพลิเคชันอย่างง่ายสำหรับบันทึกและจัดการข้อมูลการเงินส่วนบุคคล ประกอบด้วยขั้นตอนบังคับล็อกอิน การกรอกข้อมูล และการดาวน์โหลดข้อมูลเป็นไฟล์ Excel ตามที่ต้องการ พร้อมแสดงยอดรวมรายรับ รายจ่าย และคงเหลือแบบเรียลไทม์บนแดชบอร์ด

## คุณสมบัติ

- หน้าล็อกอินและสมัครสมาชิกก่อนเข้าถึงข้อมูล
- แบบฟอร์มบันทึกข้อมูลการเงิน (วันที่ ประเภท รายละเอียด จำนวนเงิน)
- แสดงข้อมูลที่บันทึกไว้ในรูปแบบตาราง พร้อมสรุปยอดรวมรายรับ/รายจ่าย/คงเหลือ
- ส่งออกข้อมูลที่กรองตามผู้ใช้เป็นไฟล์ Excel ได้ทันที (มีสรุปยอดรวมท้ายไฟล์)
=======
เว็บแอปพลิเคชันอย่างง่ายสำหรับบันทึกและจัดการข้อมูลการเงินส่วนบุคคล ประกอบด้วยขั้นตอนบังคับล็อกอิน การกรอกข้อมูล และการดาวน์โหลดข้อมูลเป็นไฟล์ Excel ตามที่ต้องการ

## คุณสมบัติ

- หน้าล็อกอินและสมัครสมาชิกก่อนเข้าถึงข้อมูล
- แบบฟอร์มบันทึกข้อมูลการเงิน (วันที่ ประเภท รายละเอียด จำนวนเงิน)
- แสดงข้อมูลที่บันทึกไว้ในรูปแบบตาราง
- ส่งออกข้อมูลที่กรองตามผู้ใช้เป็นไฟล์ Excel ได้ทันที
 main

## การติดตั้ง

1. สร้าง virtual environment (แนะนำ):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # บน Windows ใช้ .venv\\Scripts\\activate
   ```

codex/create-web-app-with-login-and-data-export-ruoc1c
2. ติดตั้ง dependencies ที่จำเป็นสำหรับรันระบบ:
=======
2. ติดตั้ง dependencies ที่จำเป็น:
main

   ```bash
   pip install -r requirements.txt
   ```

codex/create-web-app-with-login-and-data-export-ruoc1c
3. (ตัวเลือก) ติดตั้งเครื่องมือสำหรับแพ็กเป็นไฟล์ `.exe`:

   ```bash
   pip install -r requirements-dev.txt
   ```

4. (ตัวเลือก) ตั้งค่า Secret Key และตำแหน่งฐานข้อมูลผ่านไฟล์ `.env` หรือ environment variables:

   ```env
   FLASK_SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///your-custom.db  # หากต้องการใช้ฐานข้อมูลอื่น
   FINANCE_APP_STORAGE_DIR=C:/Users/you/FinanceAppData  # โฟลเดอร์เก็บไฟล์ SQLite เมื่อไม่ตั้งค่า DATABASE_URL
   PORT=5000  # ปรับพอร์ตเซิร์ฟเวอร์ (ใช้กับ start_app.py และไฟล์ .exe)
   ```

## การใช้งาน

### โหมดพัฒนา (เหมาะสำหรับนักพัฒนา)

=======
3. (ทางเลือก) ตั้งค่า Secret Key และฐานข้อมูลผ่านไฟล์ `.env` หรือ environment variables:

   ```env
   FLASK_SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///finance.db  # ค่าเริ่มต้นหากไม่ระบุ
   ```

## การใช้งาน

main
1. รันแอปพลิเคชัน:

   ```bash
   flask --app app:create_app run
   ```

   หรือใช้ `python run.py` สำหรับโหมดพัฒนา (มี `debug=True`).

2. เปิดเบราว์เซอร์และเข้าที่ `http://127.0.0.1:5000`

codex/create-web-app-with-login-and-data-export-ruoc1c
### โหมดเดสก์ท็อป (เหมาะสำหรับผู้ใช้ทั่วไป)

1. รันคำสั่ง:

   ```bash
   python start_app.py
   ```

   คำสั่งนี้จะเปิดเซิร์ฟเวอร์ Flask แบบไม่เปิดโหมด debug ที่ `127.0.0.1` และเปิดเบราว์เซอร์อัตโนมัติ เมื่อใช้งานเสร็จให้กด `Ctrl+C` เพื่อปิดโปรแกรม

2. ลงชื่อสมัครและเข้าสู่ระบบ กรอกข้อมูลการเงินผ่านแบบฟอร์ม และกด “ดาวน์โหลด Excel” เพื่อรับไฟล์ `.xlsx`

> หมายเหตุ: เมื่อสร้างไฟล์ `.exe` ผู้ใช้ปลายทางเพียงดับเบิลคลิกที่ `FinanceTracker.exe` จะได้ผลลัพธ์เหมือนกับการรัน `python start_app.py`
=======
3. สมัครสมาชิกผู้ใช้ใหม่ (หากยังไม่มีบัญชี) จากนั้นเข้าสู่ระบบ

4. บันทึกข้อมูลการเงินผ่านแบบฟอร์มและตรวจสอบผลในตารางด้านข้าง

5. กดปุ่ม “ดาวน์โหลด Excel” เพื่อดาวน์โหลดไฟล์ `.xlsx` ที่รวมข้อมูลทั้งหมดของผู้ใช้ปัจจุบัน
main

## โครงสร้างฐานข้อมูล

แอปใช้ SQLite (ผ่าน SQLAlchemy) โดยมีตารางหลัก 2 ตาราง:

- `users`: เก็บชื่อผู้ใช้และรหัสผ่าน (เข้ารหัสด้วย `werkzeug.security`)
- `finance_records`: เก็บบันทึกการเงินที่สัมพันธ์กับผู้ใช้แต่ละคน

## หมายเหตุ

- ข้อมูลทุกอย่างถูกแยกตามบัญชีผู้ใช้ ปลอดภัยด้วย session และการตรวจสอบสิทธิ์ผ่าน `Flask-Login`
- หากต้องการใช้งานใน production ควรเปลี่ยน `SECRET_KEY` และพิจารณาการใช้งานฐานข้อมูลภายนอกแทน SQLite
codex/create-web-app-with-login-and-data-export-ruoc1c
- ค่าเริ่มต้นของฐานข้อมูลจะถูกเก็บไว้ที่โฟลเดอร์ `~/FinanceTrackerData/finance.db` (หรือ `%USERPROFILE%\FinanceTrackerData\finance.db` บน Windows) สามารถเปลี่ยนตำแหน่งได้ด้วยตัวแปร `FINANCE_APP_STORAGE_DIR`

## การทดสอบ

ติดตั้ง dependencies สำหรับนักพัฒนาด้วย `pip install -r requirements-dev.txt` (มีทั้ง PyInstaller และ Pytest) แล้วรันคำสั่ง:

```bash
pytest
```

คำสั่งนี้จะทดสอบขั้นตอนสำคัญ ได้แก่ การสมัครสมาชิก การเข้าสู่ระบบ การบันทึกข้อมูลทางการเงิน และการดาวน์โหลดไฟล์ Excel ที่มีข้อมูลสรุปท้ายไฟล์

## การสร้างไฟล์ .exe สำหรับ Windows

1. ติดตั้ง dependencies สำหรับการ build (หากยังไม่ได้ทำ):

   ```bash
   pip install -r requirements-dev.txt
   ```

2. รันสคริปต์แพ็กแอป:

   ```bash
   python build_executable.py
   ```

   PyInstaller จะสร้างโฟลเดอร์ `dist/FinanceTracker` ซึ่งประกอบด้วยไฟล์ `FinanceTracker.exe` และ asset ทั้งหมดที่จำเป็น

3. (ตัวเลือก) เตรียมไฟล์สำหรับ Release:

   - บีบอัดโฟลเดอร์ `dist/FinanceTracker` เป็น `.zip`
   - อัปโหลดไฟล์ `.zip` ไปยัง GitHub Releases หรือแพลตฟอร์มที่ต้องการ

4. การใช้งานฝั่งผู้ใช้:

   - แตกไฟล์ `.zip`
   - ดับเบิลคลิก `FinanceTracker.exe`
   - เบราว์เซอร์จะเปิดไปยัง `http://127.0.0.1:<PORT>/`
   - ข้อมูลจะถูกเก็บไว้ในโฟลเดอร์ `FinanceTrackerData` ภายใต้โฟลเดอร์ผู้ใช้ โดยสามารถวางไฟล์ `.env` ไว้ข้าง `FinanceTracker.exe` เพื่อปรับตั้งค่า (เช่น `FLASK_SECRET_KEY`, `FINANCE_APP_STORAGE_DIR`, หรือ `PORT`)
=======
main
