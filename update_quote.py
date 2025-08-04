import random

# اقرأ ملف README
with open("README.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

# اقرأ ملف الاقتباسات
with open("quotes.txt", "r", encoding="utf-8") as f:
    quotes = f.read().split("\n---\n")

# اختر اقتباس عشوائي
quote = random.choice(quotes).strip()

# حدد القسم الخاص بالاقتباس داخل README (بين <!--QUOTE_START--> و <!--QUOTE_END-->)
start_idx = end_idx = -1
for i, line in enumerate(lines):
    if "<!--QUOTE_START-->" in line:
        start_idx = i + 1
    if "<!--QUOTE_END-->" in line:
        end_idx = i
        break

# استبدل الاقتباس الحالي بالجديد
if start_idx != -1 and end_idx != -1:
    lines[start_idx:end_idx] = [f'  <em>{quote.split("–")[0].strip()}</em>  
  <br>– {quote.split("–")[1].strip()}
']

# اكتب التحديث في README
with open("README.md", "w", encoding="utf-8") as f:
    f.writelines(lines)