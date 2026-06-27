# Write your code here :-)
# پروژه ۷ (نسخه ۴.۲): نسخه نهایی و فوق‌العاده هوشمند برای خواندن مستقیم فایل اکسل بدون نیاز به پانداس
import os
import zipfile
import xml.etree.ElementTree as ET

excel_file = "Coatings_db.xlsx"

# ۱. چک کردن وجود فایل در پوشه
if not os.path.exists(excel_file):
    print(f"❌ Error: Could not find '{excel_file}' in this folder!")
    print(f"Current Folder: {os.getcwd()}")
    exit()

def parse_excel_without_pandas(file_path):
    """یک تابع بومی برای باز کردن هسته فایل اکسل و استخراج داده‌های متالورژیکی"""
    coatings = {}
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            # خواندن رشته‌های متنی اکسل
            strings_xml = z.read('xl/sharedStrings.xml')
            strings_root = ET.fromstring(strings_xml)
            strings = [node.text for node in strings_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')]

            # خواندن دیتای شیت اول
            sheet_xml = z.read('xl/worksheets/sheet1.xml')
            sheet_root = ET.fromstring(sheet_xml)

            for row_node in sheet_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                row_cells = []
                for cell_node in row_node.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    val_node = cell_node.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    if val_node is not None:
                        val = val_node.text
                        if cell_node.get('t') == 's':  # اگر متن بود
                            val = strings[int(val)]
                        row_cells.append(val.strip())

                # فیلتر کردن ردیف‌های خالی و استخراج داده‌ها
                if row_cells and row_cells[0].isdigit():
                    code = row_cells[0]
                    name = row_cells[1]

                    # پیدا کردن عدد hours_Per_Micron در میان سلول‌ها
                    rating = None
                    for item in row_cells[2:]:
                        try:
                            rating = float(item)
                            break
                        except ValueError:
                            continue

                    # پیدا کردن استاندارد (معمولاً سلول بعد از عدد یا انتهای سطر)
                    standard = "ASTM B117 / ISO 9227"
                    for item in row_cells:
                        if "ISO" in item or "ASTM" in item or "MIL" in item:
                            standard = item
                            break

                    app = row_cells[-1] if len(row_cells) > 4 else "Industrial Tooling"

                    if rating:
                        coatings[code] = {"name": name, "rating": rating, "standard": standard, "app": app}
    except Exception as e:
        print(f"❌ Detail Error parsing Excel: {e}")
    return coatings

# ۲. اجرای موتور استخراج داده
coatings_data = parse_excel_without_pandas(excel_file)

if not coatings_data:
    print("❌ Error: Database loaded but no valid rows found. Check your Excel layout.")
    exit()

# ۳. نمایش منوی نهایی و مهندسی
print("==================================================================")
print("   EXCEL-DRIVEN COATING LIFETIME SIMULATOR v4.2 (Native Engine)  ")
print("==================================================================")
print("Available Coatings Loaded from Coatings_db.xlsx:")
print(f"{'Code':<6}{'Coating Name':<45}{'Standard Ref'}")
print("------------------------------------------------------------------")
for code, data in coatings_data.items():
    print(f" [{code:<3}] {data['name'][:43]:<45} {data['standard']}")
print("------------------------------------------------------------------")

# ۴. بخش تعاملی با کاربر
user_choice = input("Select coating code from the list: ").strip()
thickness = float(input("Enter coating thickness (microns): "))

print("\nSelect Operating Environment:")
print("1. Mild (Dry/Urban)")
print("2. Marine (Coastal/High Salinity)")
print("3. Severe (Industrial/Winter Road Salting)")
env_choice = input("Choose environment (1-3): ")

if user_choice in coatings_data:
    selected = coatings_data[user_choice]
    predicted_hours = thickness * selected["rating"]

    if env_choice == "1":
        env_factor, env_name = 1.0, "Mild (Urban)"
    elif env_choice == "2":
        env_factor, env_name = 0.7, "Marine (Coastal)"
    else:
        env_factor, env_name = 0.5, "Severe (Road Salt / Industrial)"

    estimated_years = (predicted_hours / 100) * env_factor

    print("\n------------------- METALLURGICAL QC REPORT -------------------")
    print(f"-> Selected Coating   : {selected['name']}")
    print(f"-> Coating Thickness  : {thickness} µm")
    print(f"-> Standard Reference : {selected['standard']}")
    print(f"-> Typical Evaluation : {selected['app']}")
    print(f"-> Target Environment : {env_name}")
    print("----------------------------------------------------------------")
    print(f"⏳ PREDICTED ASTM B117 RESISTANCE : {predicted_hours:.0f} Hours")
    print(f"🚗 ESTIMATED REAL-WORLD LIFETIME  : {estimated_years:.1f} Years")
    print("----------------------------------------------------------------")

    if predicted_hours >= 720:
        print("📢 VERDICT: APPROVED FOR HIGH-EXPOSURE CHASSIS & AEROSPACE USE ⭐")
    elif 480 <= predicted_hours < 720:
        print("📢 VERDICT: APPROVED FOR AUTOMOTIVE EXTERIOR BODY PANELS ✅")
    elif 240 <= predicted_hours < 480:
        print("📢 VERDICT: APPROVED FOR UNDER-HOOD / SEMI-PROTECTED PARTS 🟡")
    else:
        print("📢 VERDICT: REJECTED FOR OUTDOOR USE ❌")
    print("==================================================================")
else:
    print("❌ Error: Code not found in database.")
