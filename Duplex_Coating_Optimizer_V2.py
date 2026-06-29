# Write your code here :-)
# پروژه هشتم (نسخه ۲.۰): سامانه خبره و پیشنهاددهنده هوشمند پوشش‌های چندلایه صنعتی
import os
import zipfile
import xml.etree.ElementTree as ET
import math

excel_file = "Coatings_db.xlsx"

if not os.path.exists(excel_file):
    print(f"❌ Error: '{excel_file}' not found in this folder!")
    exit()

def parse_advanced_excel(file_path):
    """موتور بومی برای استخراج کامل دیتابیس غنی‌شده پوشش‌ها از اکسل"""
    coatings = {}
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            strings_xml = z.read('xl/sharedStrings.xml')
            strings_root = ET.fromstring(strings_xml)
            strings = [node.text for node in strings_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')]

            sheet_xml = z.read('xl/worksheets/sheet1.xml')
            sheet_root = ET.fromstring(sheet_xml)

            for row_node in sheet_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                row_cells = []
                for cell_node in row_node.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    val_node = cell_node.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    if val_node is not None:
                        val = val_node.text
                        if cell_node.get('t') == 's':
                            val = strings[int(val)]
                        row_cells.append(val.strip())

                if row_cells and row_cells[0].isdigit():
                    code = row_cells[0]
                    name = row_cells[1]
                    rate = float(row_cells[2])
                    potential = float(row_cells[3])
                    c_type = row_cells[4]
                    standard = row_cells[5]
                    app = row_cells[6] if len(row_cells) > 6 else ""

                    coatings[code] = {
                        "name": name, "rate": rate, "potential": potential,
                        "type": c_type, "standard": standard, "app": app
                    }
    except Exception as e:
        print(f"❌ Error reading rich database: {e}")
    return coatings

# بارگذاری دیتابیس
coatings_db = parse_advanced_excel(excel_file)

if not coatings_db:
    print("❌ Error: Could not parse database. Check your Excel structure.")
    exit()

print("==================================================================")
print("   AI-DRIVEN METALLURGICAL COATING RECOMMENDATION SYSTEM v2.0    ")
print("==================================================================")

# ۱. دریافت فاکتورهای کینتیکی و محیطی از مهندس بازرس
target_app = input("Enter target application keyword (e.g., fastener, chassis, automotive, valve): ").strip().lower()
humidity = float(input("Enter Average Relative Humidity (RH%): "))
temperature = float(input("Enter Operating Temperature (Celsius): "))
chloride = float(input("Enter Chloride Concentration (PPM): "))

# ۲. موتور محاسبات کینتیک خوردگی (Kinetic Corrosion Model)
# محاسبه ضریب تخریب محیطی بر اساس فرمول‌های آرنیوس و رطوبت
if humidity < 40:
    env_severity = 0.1  # رطوبت زیر 40 درصد عملاً خوردگی اتمسفری را متوقف می‌کند
else:
    # افزایش سرعت خوردگی به صورت نمایی با افزایش دما و غلظت کلراید
    temp_factor = math.exp((temperature - 25) / 10)
    chloride_factor = 1 + (chloride / 100)
    env_severity = ((humidity - 40) / 60) * temp_factor * chloride_factor

# ۳. فیلتر کردن پوشش‌های مناسب بر اساس کلمه کلیدی کاربرد
suitable_coatings = []
for code, info in coatings_db.items():
    if target_app in info["app"].lower() or target_app in info["name"].lower():
        suitable_coatings.append(code)

# اگر هیچ پوششی پیدا نشد، کل دیتابیس را در نظر بگیر
if not suitable_coatings:
    suitable_coatings = list(coatings_db.keys())

# ۴. الگوریتم جفت‌سازی هوشمند (Duplex Pairing Engine)
best_pair = None
max_lifetime = 0
galvanic_alert = ""

for c1 in suitable_coatings:
    for c2 in coatings_db.keys(): # لایه دوم می‌تواند هر لایه محافظ یا رنگی باشد
        if c1 == c2: continue

        layer1 = coatings_db[c1]
        layer2 = coatings_db[c2]

        # بررسی فیلتر سازگاری گالوانیکی: لایه رویی نباید به شدت کاتدی‌تر از لایه زیرین باشد
        pot_diff = abs(layer1["potential"] - layer2["potential"])
        if pot_diff > 0.25 and layer2["type"] == "Cathodic":
            continue # حذف جفت‌های خطرناک گالوانیکی

        # محاسبه بیس طول عمر فرضی (مثلاً با ضخامت‌های استاندارد پیش‌فرض: لایه اول 15 میکرون، لایه دوم 10 میکرون)
        t1, t2 = 15.0, 10.0
        calculated_hours = (t1 * layer1["rate"]) + (t2 * layer2["rate"])

        # اعمال ضریب هم‌افزایی (Synergy Factor) برای ترکیب آند + ترسیب سدی (مثل زینک + اپوکسی)
        synergy = 1.0
        if layer1["type"] == "Anodic" and layer2["type"] == "Barrier":
            synergy = 1.6

        final_hours = calculated_hours * synergy
        real_years = (final_hours / 100) / env_severity

        if real_years > max_lifetime:
            max_lifetime = real_years
            best_pair = (c1, c2, final_hours, pot_diff, synergy)

# ۵. چاپ گزارش مشاوره فنی مهندسی
print("\n" + "="*15 + " METALLURGICAL EXPERT SYSTEM RECOMMENDATION " + "="*15)
if best_pair:
    c1_code, c2_code, f_hours, p_diff, syn = best_pair
    l1 = coatings_db[c1_code]
    l2 = coatings_db[c2_code]

    print(f"🎯 RECOMMENDED DUPLEX SYSTEM FOR '{target_app.upper()}':")
    print(f"   -> LAYER 1 (Base Layer) : {l1['name']} ({l1['standard']})")
    print(f"   -> LAYER 2 (Top Coat)   : {l2['name']} ({l2['standard']})")
    print("------------------------------------------------------------------")
    print(f"🌡️ Calculated Environmental Severity Factor : {env_severity:.2f}")
    print(f"⚡ Galvanic Risk Potential Difference      : {p_diff:.2f} V (Safe)")
    if syn > 1.0:
        print(f"✨ Layer Synergy Coating Bonus             : +60% Lifetime Extension Activated")
    print("------------------------------------------------------------------")
    print(f"⏳ ESTIMATED ACCELERATED SALT SPRAY       : {f_hours:.0f} Hours")
    print(f"🚗 PREDICTED REAL-WORLD LIFETIME IN FIELD : {max_lifetime:.1f} Years")
    print("==================================================================")
else:
    print("❌ No safe coating combination could be matched for this specific application.")
    print("Consider changing application keywords or lowering environmental constraints.")
