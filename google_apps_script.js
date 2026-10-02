// ====================================================================
// 🚀 GOOGLE APPS SCRIPT: JOB APPLICATION AUTOMATIC TRACKER
// ====================================================================
// Cara Pakai:
// 1. Buka Google Spreadsheet baru (beri judul: "Job Tracker").
// 2. Klik menu "Extensions" (Ekstensi) -> "Apps Script".
// 3. Hapus semua kode yang ada, lalu COPY-PASTE seluruh kode ini.
// 4. Klik tombol "Deploy" (Terapkan) di kanan atas -> "New deployment".
// 5. Pilih icon Gear ⚙️ -> pilih "Web app".
// 6. Konfigurasi:
//    - Description: Job Tracker Webhook
//    - Execute as: Me (email kamu)
//    - Who has access: Anyone (Siapa saja)  <-- PENTING!
// 7. Klik "Deploy" -> Salin "Web App URL" yang diberikan.
// 8. Masukkan Web App URL tersebut ke file .env / Secret GitHub!
// ====================================================================

function doGet(e) {
  return handleRequest(e.parameter);
}

function doPost(e) {
  var data = {};
  if (e.postData && e.postData.contents) {
    try {
      data = JSON.parse(e.postData.contents);
    } catch(err) {
      data = e.parameter;
    }
  } else {
    data = e.parameter;
  }
  return handleRequest(data);
}

function handleRequest(params) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();
  
  // Buat header jika sheet masih kosong
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "Tanggal Lamar",
      "Posisi (Title)",
      "Perusahaan (Company)",
      "Lokasi",
      "Link Lowongan",
      "Status",
      "Catatan / Follow Up"
    ]);
    sheet.getRange(1, 1, 1, 7).setBackground("#1B365D").setFontColor("#FFFFFF").setFontWeight("bold");
    sheet.setFrozenRows(1);
  }
  
  var title = params.title || "Unknown Position";
  var company = params.company || "-";
  var location = params.location || "-";
  var url = params.url || "-";
  var dateStr = Utilities.formatDate(new Date(), "GMT+7", "yyyy-MM-dd HH:mm:ss");
  
  // Tambah baris data lamaran baru
  sheet.appendRow([
    dateStr,
    title,
    company,
    location,
    url,
    "Applied (Menunggu Respon)",
    ""
  ]);
  
  var html = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Job Tracker Success</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f0fdf4; }
          .card { background: white; padding: 2.5rem; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); text-align: center; max-width: 420px; width: 90%; }
          .icon { font-size: 54px; margin-bottom: 12px; }
          h2 { color: #166534; margin: 0 0 8px; font-size: 22px; }
          p { color: #4b5563; font-size: 14px; margin: 6px 0; }
          .badge { background: #dcfce7; color: #15803d; font-weight: 600; padding: 8px 14px; border-radius: 8px; display: inline-block; margin: 12px 0; font-size: 14px; }
          .btn { display: inline-block; margin-top: 15px; padding: 10px 20px; background: #0a66c2; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px; }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="icon">✅</div>
          <h2>Berhasil Dicatat!</h2>
          <p>Lamaran kerja kamu sudah otomatis tersimpan rapi ke Google Spreadsheet.</p>
          <div class="badge">💼 ${title}<br>🏢 ${company}</div>
          <br>
          <p style="font-size: 12px; color: #9ca3af;">Status: Applied (Menunggu Respon)</p>
          <a href="${url}" target="_blank" class="btn">Buka Loker LinkedIn</a>
        </div>
      </body>
    </html>
  `;
  
  return HtmlService.createHtmlOutput(html).setTitle("Lamaran Berhasil Dicatat");
}
