# FINAL PRO VERSION WITH SIGNATURE + STAMP + ONLINE

from flask import Flask, render_template_string, request, send_file, redirect
from reportlab.platypus import *
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
import os, datetime, urllib.parse
import qrcode

app = Flask(__name__)

BASE_URL = "https://academy-app-lco1.onrender.com"

LOGO = "logo_circle.png"
SIGN = "signature.png"
STAMP = "stamp.png"

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

def create_pdf(name, amount, date, month, note):

    num = get_receipt_number()

    folder = "receipts"
    if not os.path.exists(folder):
        os.makedirs(folder)

    file = f"{folder}/facture_{num}.pdf"

    doc = SimpleDocTemplate(file, pagesize=A5)
    style = ParagraphStyle(name="normal", fontSize=11)

    content = []

    # HEADER
    if os.path.exists(LOGO):
        content.append(Image(LOGO, 60, 60))

    content.append(Paragraph(f"وصل رقم {num}", style))
    content.append(Spacer(1,10))

    # TABLE
    data = [
        ["البيانات", "المعطيات"],
        ["الاسم", name],
        ["المبلغ", f"{amount} درهم"],
        ["الشهر", month],
        ["ملاحظة", note],
    ]

    content.append(Table(data))
    content.append(Spacer(1,15))

    # QR
    filename = file.split("/")[-1]
    link = f"{BASE_URL}/receipt/{filename}"

    qr = generate_qr(link)
    content.append(Image(qr, 70, 70))
    content.append(Spacer(1,15))

    # SIGNATURE + STAMP
    row = []

    if os.path.exists(SIGN):
        row.append(Image(SIGN, 100, 50))
    else:
        row.append("")

    if os.path.exists(STAMP):
        row.append(Image(STAMP, 80, 80))
    else:
        row.append("")

    content.append(Table([row]))
    content.append(Spacer(1,5))

    content.append(Paragraph("توقيع الإدارة وختم المؤسسة", style))

    doc.build(content)

    return file

@app.route('/receipt/<filename>')
def get_receipt(filename):
    return send_file(f"receipts/{filename}")

HTML = '''
<html>
<body style="text-align:center">
<h3>📄 وصل الأداء</h3>

<form method="POST">
<input name="name" placeholder="الاسم الكامل" required><br>
<input name="amount" placeholder="المبلغ" required><br>
<input name="date" value="{{date}}" required><br>
<input name="month" placeholder="الشهر"><br>
<input name="note" placeholder="ملاحظة"><br>

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
        note = request.form["note"]

        pdf = create_pdf(name, amount, date, month, note)
        filename = pdf.split("/")[-1]

        if request.form["action"] == "pdf":
            return send_file(pdf, as_attachment=True)
        else:
            link = f"{BASE_URL}/receipt/{filename}"

            msg = f"""وصل الأداء:
الاسم: {name}
المبلغ: {amount} درهم

تحميل الوصل:
{link}
"""
            url = "https://wa.me/?text=" + urllib.parse.quote(msg)
            return redirect(url)

    return render_template_string(HTML, date=datetime.date.today())

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5001)
