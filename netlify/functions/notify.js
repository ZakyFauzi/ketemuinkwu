const nodemailer = require("nodemailer");

function json(statusCode, payload, headers = {}) {
  return {
    statusCode,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "Content-Type",
      ...headers,
    },
    body: JSON.stringify(payload),
  };
}

function getEnv(key) {
  return String(process.env[key] || "").trim();
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function buildNotificationData(type, owner, finderName, messageText, mapsUrl, pageUrl) {
  const itemName = owner?.item_name || "Barang";
  const ownerName = owner?.owner_name || "Pemilik";
  const title = type === "location"
    ? "Update lokasi penemuan barang"
    : "Pesan baru dari penemu barang";
  const subtitle = type === "location"
    ? "Seseorang membagikan titik lokasi penemuan barang Anda."
    : "Seseorang mengirimkan pesan terkait barang Anda.";

  return {
    itemName,
    ownerName,
    title,
    subtitle,
    finderName: finderName || "Penemu",
    messageText: messageText || "-",
    mapsUrl: mapsUrl || "-",
    pageUrl: pageUrl || "-",
    type,
  };
}

function buildEmailText(data) {
  const lines = [
    "KETEMUIN - NOTIFIKASI BARU",
    "",
    data.title,
    data.subtitle,
    "",
    `Pemilik: ${data.ownerName}`,
    `Barang: ${data.itemName}`,
    `Dari: ${data.finderName}`,
  ];

  if (data.type === "message") {
    lines.push(`Pesan: ${data.messageText}`);
  }

  if (data.type === "location") {
    lines.push(`Lokasi: ${data.mapsUrl}`);
  }

  lines.push(`Profil: ${data.pageUrl}`);
  lines.push("");
  lines.push("Pesan ini dikirim otomatis oleh sistem Ketemuin.");

  return lines.join("\n");
}

function buildEmailHtml(data) {
  const rows = [
    { label: "Pemilik", value: escapeHtml(data.ownerName) },
    { label: "Barang", value: escapeHtml(data.itemName) },
    { label: "Dari", value: escapeHtml(data.finderName) },
  ];

  if (data.type === "message") {
    rows.push({ label: "Pesan", value: escapeHtml(data.messageText) });
  }

  if (data.type === "location") {
    rows.push({
      label: "Lokasi",
      value: `<a href="${escapeHtml(data.mapsUrl)}" target="_blank" rel="noopener noreferrer">Buka Google Maps</a>`,
    });
  }

  rows.push({
    label: "Profil",
    value: `<a href="${escapeHtml(data.pageUrl)}" target="_blank" rel="noopener noreferrer">Lihat Halaman Profil</a>`,
  });

  const rowHtml = rows
    .map((row) => `
      <tr>
        <td style="padding:10px 12px; border:1px solid #d8e2ee; width:140px; color:#4f6480; font-weight:600;">${row.label}</td>
        <td style="padding:10px 12px; border:1px solid #d8e2ee; color:#16304d;">${row.value}</td>
      </tr>`)
    .join("");

  return `
  <!doctype html>
  <html lang="id">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notifikasi Ketemuin</title>
  </head>
  <body style="margin:0; padding:0; background:#f2f5f8; font-family:Segoe UI, Tahoma, Arial, sans-serif; color:#16304d;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f2f5f8; padding:24px 10px;">
      <tr>
        <td align="center">
          <table role="presentation" width="640" cellspacing="0" cellpadding="0" style="max-width:640px; background:#ffffff; border:1px solid #d8e2ee; border-radius:12px; overflow:hidden;">
            <tr>
              <td style="background:linear-gradient(120deg,#0b467f 0%, #0f6ecd 100%); padding:20px 24px; color:#ffffff;">
                <div style="font-size:12px; letter-spacing:0.08em; text-transform:uppercase; opacity:0.9;">Ketemuin</div>
                <h1 style="margin:6px 0 0; font-size:22px; line-height:1.25;">${escapeHtml(data.title)}</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:20px 24px 8px; color:#4f6480; font-size:14px;">${escapeHtml(data.subtitle)}</td>
            </tr>
            <tr>
              <td style="padding:8px 24px 20px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse; font-size:14px;">
                  ${rowHtml}
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding:0 24px 20px; font-size:12px; color:#6b7f97;">
                Pesan ini dikirim otomatis oleh sistem Ketemuin. Mohon jangan membalas email ini.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
  </html>`;
}

function buildTelegramText(data) {
  const sections = [
    "KETEMUIN - NOTIFIKASI BARU",
    `${data.title}`,
    "",
    `Pemilik: ${data.ownerName}`,
    `Barang: ${data.itemName}`,
    `Dari: ${data.finderName}`,
  ];

  if (data.type === "message") {
    sections.push(`Pesan: ${data.messageText}`);
  }

  if (data.type === "location") {
    sections.push(`Lokasi: ${data.mapsUrl}`);
  }

  sections.push(`Profil: ${data.pageUrl}`);
  sections.push("Sistem Ketemuin");

  return sections.join("\n");
}

async function sendTelegramMessage(text, target, botToken) {
  if (!target || !botToken) {
    return { sent: false, skipped: true, reason: "missing_target_or_token" };
  }

  const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: target,
      text,
      disable_web_page_preview: false,
    }),
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok || payload.ok === false) {
    return {
      sent: false,
      error: payload.description || `Telegram request failed with status ${response.status}`,
    };
  }

  return { sent: true };
}

exports.handler = async (event) => {
  if (event.httpMethod === "OPTIONS") {
    return json(204, { ok: true });
  }

  if (event.httpMethod !== "POST") {
    return json(405, { error: "Method not allowed" });
  }

  let body = {};
  try {
    body = JSON.parse(event.body || "{}");
  } catch {
    return json(400, { error: "Invalid JSON body" });
  }

  const { type, owner, finderName, messageText, mapsUrl, pageUrl } = body;

  if (!owner || !type || !["location", "message"].includes(type)) {
    return json(400, { error: "Invalid payload" });
  }

  const emailSender = getEnv("EMAIL_SENDER");
  const emailPassword = getEnv("EMAIL_PASSWORD");
  const smtpServer = getEnv("SMTP_SERVER");
  const smtpPort = Number(getEnv("SMTP_PORT") || 587);
  const telegramToken = getEnv("TELEGRAM_BOT_TOKEN");

  const emailTarget = String(owner.owner_email || "").trim();
  const telegramTarget = String(owner.owner_telegram || "").trim();
  const whatsappTarget = String(owner.owner_whatsapp || "").trim();

  const data = buildNotificationData(type, owner, finderName, messageText, mapsUrl, pageUrl);
  const textForEmail = buildEmailText(data);
  const htmlForEmail = buildEmailHtml(data);
  const textForTelegram = buildTelegramText(data);

  const results = {
    email: { sent: false, skipped: true },
    telegram: { sent: false, skipped: true },
    whatsapp: { sent: false, skipped: true },
  };

  if (emailTarget && emailSender && emailPassword && smtpServer) {
    try {
      const transporter = nodemailer.createTransport({
        host: smtpServer,
        port: smtpPort,
        secure: smtpPort === 465,
        auth: {
          user: emailSender,
          pass: emailPassword,
        },
      });

      await transporter.sendMail({
        from: `Ketemuin <${emailSender}>`,
        to: emailTarget,
        subject: type === "location"
          ? `[Ketemuin] Update Lokasi: ${data.itemName}`
          : `[Ketemuin] Pesan Baru: ${data.itemName}`,
        text: textForEmail,
        html: htmlForEmail,
      });

      results.email = { sent: true };
    } catch (error) {
      results.email = { sent: false, error: error.message };
    }
  } else {
    results.email = { sent: false, skipped: true, reason: "missing_email_config_or_target" };
  }

  if (telegramTarget && telegramToken) {
    try {
      const telegramResult = await sendTelegramMessage(textForTelegram, telegramTarget, telegramToken);
      if (telegramResult.sent) {
        results.telegram = { sent: true };
      } else {
        results.telegram = { sent: false, error: telegramResult.error || telegramResult.reason || "Telegram skipped" };
      }
    } catch (error) {
      results.telegram = { sent: false, error: error.message };
    }
  } else {
    results.telegram = { sent: false, skipped: true, reason: "missing_telegram_config_or_target" };
  }

  if (whatsappTarget) {
    try {
      const whatsappLink = `https://api.whatsapp.com/send?phone=${encodeURIComponent(whatsappTarget)}&text=${encodeURIComponent(textForTelegram)}`;
      results.whatsapp = {
        sent: true,
        note: "WhatsApp link generated",
        link: whatsappLink,
      };
    } catch (error) {
      results.whatsapp = { sent: false, error: error.message };
    }
  } else {
    results.whatsapp = { sent: false, skipped: true, reason: "missing_whatsapp_target" };
  }

  const success = Boolean(results.email.sent || results.telegram.sent || results.whatsapp.sent);
  if (!success) {
    return json(502, {
      error: "No notification channel succeeded",
      results,
    });
  }

  return json(200, {
    ok: true,
    results,
  });
};