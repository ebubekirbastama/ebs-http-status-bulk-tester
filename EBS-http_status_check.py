import subprocess
import sys

# Gerekli paketleri kontrol edip yükleyen fonksiyon
required_packages = ['requests', 'pandas', 'openpyxl']

def install_packages(packages):
    import importlib
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"{package} yüklü değil. Kuruluyor...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

install_packages(required_packages)

# -----------------------------------

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import time
import pandas as pd
import os

# Emoji ikonlar (Unicode emojiler modern sistemlerde renkli görünür)
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WAIT = "⏳"
EMOJI_INFO = "ℹ️"
EMOJI_URL = "🔗"

# Renkli buton stilleri (ttk style)
def setup_styles():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8)
    style.map("TButton",
              foreground=[('pressed', 'white'), ('active', 'white')],
              background=[('pressed', '#0052cc'), ('active', '#1a73e8')])
    
    style.configure("Primary.TButton", background="#1a73e8", foreground="white")
    style.map("Primary.TButton",
              background=[('pressed', '#0046b8'), ('active', '#005ce6')],
              foreground=[('pressed', 'white'), ('active', 'white')])
    
    style.configure("Success.TButton", background="#28a745", foreground="white")
    style.map("Success.TButton",
              background=[('pressed', '#1e7e34'), ('active', '#218838')],
              foreground=[('pressed', 'white'), ('active', 'white')])
    
    style.configure("Danger.TButton", background="#dc3545", foreground="white")
    style.map("Danger.TButton",
              background=[('pressed', '#a71d2a'), ('active', '#c82333')],
              foreground=[('pressed', 'white'), ('active', 'white')])

setup_styles()

root = tk.Tk()
root.title("🚀 Toplu HTTP Durum Kodu Tarayıcı")
root.geometry("900x700")
root.configure(bg="#f0f2f5")

log_data = []

def clear_treeview():
    for item in tree.get_children():
        tree.delete(item)

def add_log_entry(entry):
    log_data.append(entry)

def update_status(text, color="black"):
    status_label.config(text=text, foreground=color)
    root.update()

def check_url(url):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        start = time.time()
        response = requests.head(url, timeout=10, allow_redirects=True)
        elapsed = (time.time() - start) * 1000

        entry = {
            "URL": response.url,
            "Method": response.request.method,
            "Status Code": response.status_code,
            "Reason": response.reason,
            "Elapsed(ms)": round(elapsed, 2),
            "Request Headers": dict(response.request.headers),
            "Response Headers": dict(response.headers),
            "Error": None
        }
        return entry
    except requests.exceptions.RequestException as e:
        entry = {
            "URL": url,
            "Method": None,
            "Status Code": None,
            "Reason": None,
            "Elapsed(ms)": None,
            "Request Headers": None,
            "Response Headers": None,
            "Error": str(e)
        }
        return entry

def check_urls_bulk(urls):
    clear_treeview()
    log_data.clear()
    update_status(f"{EMOJI_WAIT} {len(urls)} URL kontrol ediliyor...", "orange")

    for idx, url in enumerate(urls, start=1):
        update_status(f"{EMOJI_WAIT} {idx}/{len(urls)}: {url} kontrol ediliyor...", "orange")
        entry = check_url(url.strip())
        add_log_entry(entry)
        icon = EMOJI_ERROR if entry["Error"] else EMOJI_SUCCESS
        status_val = f"{entry['Status Code']} {entry['Reason']}" if entry["Status Code"] else "-"
        tree.insert("", "end", values=(icon, entry["URL"], status_val, entry["Elapsed(ms)"] if entry["Elapsed(ms)"] else "-", entry["Error"] if entry["Error"] else ""))

    update_status(f"{EMOJI_SUCCESS} Tüm URL'ler tarandı!", "green")

def export_logs_txt(path):
    with open(path, "w", encoding="utf-8") as f:
        for entry in log_data:
            f.write(f"URL: {entry['URL']}\n")
            f.write(f"Method: {entry['Method']}\n")
            f.write(f"Status Code: {entry['Status Code']} {entry['Reason']}\n")
            f.write(f"Elapsed Time (ms): {entry['Elapsed(ms)']}\n")
            if entry['Error']:
                f.write(f"Error: {entry['Error']}\n")
            else:
                f.write("Request Headers:\n")
                for k,v in entry['Request Headers'].items():
                    f.write(f"  {k}: {v}\n")
                f.write("Response Headers:\n")
                for k,v in entry['Response Headers'].items():
                    f.write(f"  {k}: {v}\n")
            f.write("\n"+"-"*50+"\n\n")
    messagebox.showinfo("Başarılı", f"Loglar başarıyla TXT dosyasına kaydedildi:\n{path}")

def export_logs_csv(path):
    df = pd.DataFrame([{
        "URL": e["URL"],
        "Method": e["Method"],
        "Status Code": e["Status Code"],
        "Reason": e["Reason"],
        "Elapsed(ms)": e["Elapsed(ms)"],
        "Error": e["Error"]
    } for e in log_data])
    df.to_csv(path, index=False)
    messagebox.showinfo("Başarılı", f"Loglar başarıyla CSV dosyasına kaydedildi:\n{path}")

def export_logs_excel(path):
    df = pd.DataFrame([{
        "URL": e["URL"],
        "Method": e["Method"],
        "Status Code": e["Status Code"],
        "Reason": e["Reason"],
        "Elapsed(ms)": e["Elapsed(ms)"],
        "Error": e["Error"]
    } for e in log_data])
    df.to_excel(path, index=False)
    messagebox.showinfo("Başarılı", f"Loglar başarıyla Excel dosyasına kaydedildi:\n{path}")

def export_logs_html(path):
    total = len(log_data)
    success_count = sum(1 for e in log_data if not e["Error"] and e["Status Code"] and 200 <= e["Status Code"] < 400)
    fail_count = total - success_count

    # Bootstrap 5 CSS CDN
    bootstrap_css = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">'

    # HTML Başlangıcı
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>HTTP Durum Kodu Raporu</title>
        {bootstrap_css}
        <style>
            body {{ padding: 20px; background-color: #f8f9fa; }}
            .success {{ color: green; font-weight: bold; }}
            .fail {{ color: red; font-weight: bold; }}
            .accordion-button::after {{
                font-size: 1.2rem;
            }}
            pre {{
                background-color: #e9ecef;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">🚀 HTTP Durum Kodu Raporu</h1>
            <div class="mb-3">
                <span class="badge bg-primary">Toplam URL: {total}</span>
                <span class="badge bg-success ms-2">Başarılı: {success_count}</span>
                <span class="badge bg-danger ms-2">Başarısız: {fail_count}</span>
            </div>

            <div class="accordion" id="urlAccordion">
    """

    for i, e in enumerate(log_data):
        status_text = f"{e['Status Code']} {e['Reason']}" if e['Status Code'] else "-"
        status_class = "success" if e["Error"] is None and e["Status Code"] and 200 <= e["Status Code"] < 400 else "fail"
        error_html = f"<pre>{e['Error']}</pre>" if e['Error'] else ""

        req_headers = ""
        if e['Request Headers']:
            req_headers = "<pre>" + "\n".join(f"{k}: {v}" for k, v in e['Request Headers'].items()) + "</pre>"

        res_headers = ""
        if e['Response Headers']:
            res_headers = "<pre>" + "\n".join(f"{k}: {v}" for k, v in e['Response Headers'].items()) + "</pre>"

        html_content += f"""
        <div class="accordion-item">
            <h2 class="accordion-header" id="heading{i}">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{i}" aria-expanded="false" aria-controls="collapse{i}">
                    {e['URL']} — <span class="{status_class}">{status_text}</span> — {e['Elapsed(ms)'] if e['Elapsed(ms)'] else '-'} ms
                </button>
            </h2>
            <div id="collapse{i}" class="accordion-collapse collapse" aria-labelledby="heading{i}" data-bs-parent="#urlAccordion">
                <div class="accordion-body">
                    <strong>HTTP Method:</strong> {e['Method'] if e['Method'] else '-'}<br>
                    <strong>Hata Mesajı:</strong> {error_html if error_html else '-'}<br><br>
                    <strong>İstek Başlıkları:</strong> {req_headers if req_headers else '-'}<br>
                    <strong>Yanıt Başlıkları:</strong> {res_headers if res_headers else '-'}<br>
                </div>
            </div>
        </div>
        """

    html_content += """
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)
    messagebox.showinfo("Başarılı", f"Loglar başarıyla Bootstrap destekli HTML dosyasına kaydedildi:\n{path}")

def browse_file():
    file_path = filedialog.askopenfilename(
        title="URL Listesi Dosyası Seçin",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            text_urls.delete(1.0, tk.END)
            text_urls.insert(tk.END, content)

def on_check_urls():
    urls_raw = text_urls.get(1.0, tk.END).strip()
    if not urls_raw:
        messagebox.showwarning("Uyarı", "Lütfen en az bir URL girin.")
        return
    urls = [line.strip() for line in urls_raw.splitlines() if line.strip()]
    check_urls_bulk(urls)

def on_export(format_):
    if not log_data:
        messagebox.showwarning("Uyarı", "Dışa aktarılacak veri yok.")
        return

    ext_map = {"txt": "*.txt", "csv": "*.csv", "excel": "*.xlsx", "html": "*.html"}
    filetypes_map = {
        "txt": [("Text Files", "*.txt")],
        "csv": [("CSV Files", "*.csv")],
        "excel": [("Excel Files", "*.xlsx")],
        "html": [("HTML Files", "*.html")]
    }
    save_path = filedialog.asksaveasfilename(defaultextension=ext_map[format_],
                                             filetypes=filetypes_map[format_],
                                             title=f"{format_.upper()} olarak kaydet")
    if not save_path:
        return

    if format_ == "txt":
        export_logs_txt(save_path)
    elif format_ == "csv":
        export_logs_csv(save_path)
    elif format_ == "excel":
        export_logs_excel(save_path)
    elif format_ == "html":
        export_logs_html(save_path)

# ------------------- GUI Elemanları -------------------

frame_top = ttk.Frame(root, padding=10)
frame_top.pack(fill=tk.X)

label_instructions = ttk.Label(frame_top, text="URL'leri alt alta yazın veya dosyadan yükleyin:", font=("Segoe UI", 12))
label_instructions.pack(side=tk.LEFT, padx=5)

btn_browse = ttk.Button(frame_top, text=f"{EMOJI_INFO} Dosyadan Yükle", style="Primary.TButton", command=browse_file)
btn_browse.pack(side=tk.RIGHT, padx=5)

text_urls = tk.Text(root, height=8, font=("Consolas", 11))
text_urls.pack(fill=tk.X, padx=10, pady=5)

btn_check = ttk.Button(root, text=f"{EMOJI_WAIT} Taramaya Başla", style="Success.TButton", command=on_check_urls)
btn_check.pack(pady=5)

# --- Treeview ile logları gösterme ---
columns = ("Durum", "URL", "HTTP Durum Kodu", "Geçen Süre (ms)", "Hata Mesajı")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    if col == "URL":
        tree.column(col, width=350)
    else:
        tree.column(col, width=110, anchor=tk.CENTER)

tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

status_label = ttk.Label(root, text="", font=("Segoe UI", 11, "italic"), foreground="gray")
status_label.pack(pady=5)

frame_bottom = ttk.Frame(root)
frame_bottom.pack(pady=10)

btn_export_txt = ttk.Button(frame_bottom, text="TXT Olarak Dışa Aktar", style="Primary.TButton", command=lambda: on_export("txt"))
btn_export_txt.grid(row=0, column=0, padx=10)

btn_export_csv = ttk.Button(frame_bottom, text="CSV Olarak Dışa Aktar", style="Primary.TButton", command=lambda: on_export("csv"))
btn_export_csv.grid(row=0, column=1, padx=10)

btn_export_excel = ttk.Button(frame_bottom, text="Excel Olarak Dışa Aktar", style="Primary.TButton", command=lambda: on_export("excel"))
btn_export_excel.grid(row=0, column=2, padx=10)

btn_export_html = ttk.Button(frame_bottom, text="HTML (Bootstrap) Olarak Dışa Aktar", style="Primary.TButton", command=lambda: on_export("html"))
btn_export_html.grid(row=0, column=3, padx=10)

root.mainloop()
