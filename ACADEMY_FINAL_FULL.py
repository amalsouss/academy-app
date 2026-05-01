# FINAL SYSTEM - PDF + WHATSAPP (ONLINE READY)

from flask import Flask, render_template_string, request, send_file, redirect
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, datetime, urllib.parse
import arabic_reshaper
from bidi.algorithm import get_display
from num2words import num2words
import qrcode

app = Flask(__name__)

# 🔥 رابط Render ديالك
BASE_URL = "https://academy-app-lco1.onrender.com"

FONT_PATH = "Amiri-Regular.ttf"
LOGO_PATH = "logo_circle.png"

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('Arabic', FONT_PATH))

def fix_ar(text):
    return get_display(arabic_reshaper.reshape(text))

def get_receipt_number():
    if not os.path.exists("counter.txt"):
        open("counter.txt","w").write("1")
        return 1
    n=int(open("counter.txt").read())
    open("counter.txt","w").write(str(n+1))
    return n

def generate_qr(data):
    file="qr.png"
    img=qrcode.make(data)
    img.save(file)
    return file

def draw_border(canvas, doc):
    width, height = A5
    canvas.setLineWidth(2)
    canvas.rect(10, 10, width-20, height-20)
    canvas.setLineWidth(1)
    canvas.rect(15, 15, width-30, height-30)

def create_pdf(name, amount, date, month, note):

    BLUE = colors.HexColor("#0A5F9E")
    GREEN = colors.HexColor("#00C853")

    num = get_receipt_number()

    folder = "receipts"
    if not os.path.exists(folder):
        os.makedirs(folder)

    file = f"{folder}/facture_{num}.pdf"

    doc = SimpleDocTemplate(file, pagesize=A5,
                            rightMargin=25, leftMargin=25,
                            topMargin=25, bottomMargin=25)

    title = ParagraphStyle(name="title", fontName="Arabic", fontSize=16, alignment=1, textColor=BLUE)
    subtitle = ParagraphStyle(name="sub", fontSize=10, alignment=1, textColor=GREEN)
    normal = ParagraphStyle(name="normal", fontName="Arabic", fontSize=10, alignment=2)
    center = ParagraphStyle(name="center", fontName="Arabic", fontSize=9, alignment=1)

    content = []

    logo = Image(LOGO_PATH, 50, 50) if os.path.exists(LOGO_PATH) else ""

    header = [["", Paragraph(fix_ar("أكاديمية أمل سوس لكرة القدم"), title), logo]]
    content.append(Table(header, colWidths=[60, 200, 60]))

    content.append(Spacer(1,6))
    content.append(Paragraph("Académie Amal Souss de Football", subtitle))
    content.append(Spacer(1,12))

    content.append(Table([[""]], colWidths=[260], style=[('LINEBELOW', (0,0), (-1,-1), 1.5, BLUE)]))
    content.append(Spacer(1,10))

    content.append(Paragraph(fix_ar(f"وصل أداء رقم: {num}"), normal))
    content.append(Paragraph(fix_ar(f"التاريخ: {date}"), normal))
    content.append(Spacer(1,15))

    amount_words = num2words(int(amount), lang='ar')

    data = [
        [Paragraph(fix_ar("المعطيات"), normal), Paragraph(fix_ar("البيانات"), normal)],
        [Paragraph(fix_ar(name), normal), Paragraph(fix_ar("اسم اللاعب"), normal)],
        [Paragraph(fix_ar(f"{amount} درهم"), normal), Paragraph(fix_ar("المبلغ"), normal)],
        [Paragraph(fix_ar(amount_words + " درهم"), normal), Paragraph(fix_ar("بالحروف"), normal)],
        [Paragraph(fix_ar(month), normal), Paragraph(fix_ar("الشهر"), normal)],
        [Paragraph(fix_ar(note), normal), Paragraph(fix_ar("ملاحظة"), normal)],
    ]

    table = Table(data, colWidths=[140, 120])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.6, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))

    content.append(table)
    content.append(Spacer(1,20))

    filename = file.split("/")[-1]
    link = f"{BASE_URL}/receipt/{filename}"

    qr = generate_qr(link)
    content.append(Image(qr, 70, 70))
    content.append(Spacer(1,20))

    sig = Image("signature.png", 90, 40) if os.path.exists("signature.png") else ""
    stamp = Image("stamp.png", 80, 80) if os.path.exists("stamp.png") else ""

    content.append(Table([[sig, stamp]], colWidths=[130,130]))
    content.append(Spacer(1,10))

    content.append(Table([[""]], colWidths=[260], style=[('LINEABOVE', (0,0), (-1,-1), 1.5, GREEN)]))
    content.append(Spacer(1,8))

    content.append(Paragraph(fix_ar("أكاديمية أمل سوس لكرة القدم"), center))
    content.append(Paragraph(fix_ar("المقر: شارع الادارسة زنقة 3101 رقم 76 الدشيرة الجهادية"), center))
    content.append(Paragraph(fix_ar("الهاتف: 06 31 61 66 67 / 06 87 89 51 63"), center))

    doc.build(content, onFirstPage=draw_border, onLaterPages=draw_border)

    return file

@app.route('/receipt/<filename>')
def get_receipt(filename):
    return send_file(f"receipts/{filename}")

HTML = '''
<html>
<body style="text-align:center;font-family:Arial">
<h3>📄 وصل الأداء</h3>

<form method="POST">
<input name="name" placeholder="الاسم الكامل" required><br>
<input name="amount" placeholder="المبلغ" required><br>
<input name="date" value="{{date}}" required><br>

<select name="month">
<option>يناير</option><option>فبراير</option><option>مارس</option>
<option>أبريل</option><option>ماي</option><option>يونيو</option>
<option>يوليوز</option><option>غشت</option><option>شتنبر</option>
<option>أكتوبر</option><option>نونبر</option><option>دجنبر</option>
</select><br>

<select name="note">
<option>الواجب الشهري</option>
<option>الواجب السنوي</option>
<option>رحلة</option>
</select><br>

<input name="note_custom" placeholder="أو اكتب ملاحظة أخرى"><br>

<button name="action" value="pdf">📄 تحميل PDF</button>
<button name="action" value="whatsapp">📱 إرسال WhatsApp</button>

</form>
</body>
</html>
'''

@app.route("/", methods=["GET","POST"])
def home():
    if request.method=="POST":
        name = request.form["name"]
        amount = request.form["amount"]
        date = request.form["date"]
        month = request.form["month"]
        note = request.form["note_custom"] if request.form["note_custom"] else request.form["note"]

        pdf = create_pdf(name, amount, date, month, note)
        filename = pdf.split("/")[-1]

        if request.form["action"] == "pdf":
            return send_file(pdf, as_attachment=True)
        else:
            link = f"{BASE_URL}/receipt/{filename}"
            msg = f"وصل الأداء:\nالاسم: {name}\nالمبلغ: {amount} درهم\n{link}"
            url = "https://wa.me/?text=" + urllib.parse.quote(msg)
            return redirect(url)

    return render_template_string(HTML, date=datetime.date.today())

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5001)
