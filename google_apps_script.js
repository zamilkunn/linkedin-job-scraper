// ====================================================================
// 🚀 GOOGLE APPS SCRIPT: AUTO TRACKER SESUAI FORMAT SPREADSHEET ZAMIL
// ====================================================================
// Format Kolom:
// [A] No (Nomor urut otomatis)
// [B] Company (Nama Perusahaan)
// [C] Program (Posisi / Job Title)
// [D] Type (Otomatis deteksi: MT / Intern / Contract / Fulltime)
// [E] Reff (Linkedin)
// [F] Link (URL Lowongan)
// [G] Tanggal Lamar (Format: "2 October 2026")
// [H] Progress ("Submitted")
// [I] Reason ("-")
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
  
  var company = params.company || "Perusahaan";
  var program = params.title || "Position";
  var url = params.url || "-";
  
  // Deteksi Type secara otomatis dari judul program
  var programLower = program.toLowerCase();
  var jobType = "Fulltime";
  if (programLower.includes("intern") || programLower.includes("magang")) {
    jobType = "Intern";
  } else if (programLower.includes("mt") || programLower.includes("management trainee") || programLower.includes("mdp") || programLower.includes("leap") || programLower.includes("gtp")) {
    jobType = "MT";
  } else if (programLower.includes("contract") || programLower.includes("project") || programLower.includes("staff")) {
    jobType = "Contract ";
  }

  // Format tanggal Indonesia/English seperti di sheet Zamil (contoh: "2 October 2026")
  var months = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
  ];
  var now = new Date();
  var day = now.getDate();
  var month = months[now.getMonth()];
  var year = now.getFullYear();
  var dateFormatted = day + " " + month + " " + year;

  // Cari nomor urut terakhir di kolom A
  var lastRow = sheet.getLastRow();
  var nextNo = 1;
  for (var r = lastRow; r >= 1; r--) {
    var val = sheet.getRange(r, 1).getValue();
    if (!isNaN(val) && val !== "" && typeof val === "number") {
      nextNo = Number(val) + 1;
      break;
    }
  }

  // Baris baru yang akan diinsert ke kolom A sampai I
  var newRow = [
    nextNo,           // [A] No
    company,          // [B] Company
    program,          // [C] Program
    jobType,          // [D] Type
    "Linkedin",       // [E] Reff
    url,              // [F] Link
    dateFormatted,    // [G] Tanggal Lamar
    "Submitted",      // [H] Progress
    ""                // [I] Reason
  ];

  sheet.appendRow(newRow);

  var html = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Lamaran Berhasil Dicatat</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #0f172a; color: #f8fafc; }
          .card { background: #1e293b; padding: 2rem; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); text-align: center; max-width: 440px; width: 90%; border: 1px solid #334155; }
          .icon { font-size: 48px; margin-bottom: 8px; }
          h2 { color: #38bdf8; margin: 0 0 8px; font-size: 20px; }
          p { color: #94a3b8; font-size: 14px; margin: 6px 0; }
          .badge { background: #0f172a; color: #38bdf8; border: 1px solid #0284c7; padding: 10px 14px; border-radius: 10px; display: inline-block; margin: 12px 0; font-size: 14px; text-align: left; width: 85%; }
          .row { margin: 4px 0; }
          .btn { display: inline-block; margin-top: 15px; padding: 10px 22px; background: #0a66c2; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px; }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="icon">🚀</div>
          <h2>Tercatat di Spreadsheet!</h2>
          <p>Lamaran No. <b>#${nextNo}</b> sudah otomatis masuk ke Job Tracker kamu.</p>
          <div class="badge">
            <div class="row">🏢 <b>Company:</b> ${company}</div>
            <div class="row">💼 <b>Program:</b> ${program}</div>
            <div class="row">🏷️ <b>Type:</b> ${jobType}</div>
            <div class="row">📅 <b>Tanggal:</b> ${dateFormatted}</div>
            <div class="row">📌 <b>Status:</b> Submitted</div>
          </div>
          <br>
          <a href="${url}" target="_blank" class="btn">Buka Halaman LinkedIn</a>
        </div>
      </body>
    </html>
  `;
  
  return HtmlService.createHtmlOutput(html).setTitle("Lamaran Berhasil Dicatat");
}
