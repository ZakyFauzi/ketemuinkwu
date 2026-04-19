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

function buildEmailText(type, owner, finderName, messageText, mapsUrl, pageUrl) {
  const itemName = owner?.item_name || "Barang";
  const ownerName = owner?.owner_name || "Pemilik";
  const header = type === "location"
    ? `Lokasi baru ditemukan untuk ${itemName}`
    : `Pesan baru untuk ${itemName}`;

  const lines = [
    header,
    `Pemilik: ${ownerName}`,
    `Barang: ${itemName}`,
  ];

  if (finderName) {
    lines.push(`Dari: ${finderName}`);
  }

  if (type === "location" && mapsUrl) {
    lines.push(`Maps: ${mapsUrl}`);
  }

  if (type === "message" && messageText) {
    lines.push(`Pesan: ${messageText}`);
  }

  if (pageUrl) {
    lines.push(`Profil: ${pageUrl}`);
  }

  return lines.join("\n");
}

function buildTelegramText(type, owner, finderName, messageText, mapsUrl, pageUrl) {
  const itemName = owner?.item_name || "Barang";
  const ownerName = owner?.owner_name || "Pemilik";
  const header = type === "location"
    ? `Lokasi baru untuk ${itemName}`
    : `Pesan baru untuk ${itemName}`;

  const lines = [
    `Ketemuin`,
    header,
    `Pemilik: ${ownerName}`,
  ];

  if (finderName) {
    lines.push(`Dari: ${finderName}`);
  }

  if (type === "location" && mapsUrl) {
    lines.push(`Maps: ${mapsUrl}`);
  }

  if (type === "message" && messageText) {
    lines.push(`Pesan: ${messageText}`);
  }

  if (pageUrl) {
    lines.push(`Profil: ${pageUrl}`);
  }

  return lines.join("\n");
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

  const {
    type,
    owner,
    finderName,
    messageText,
    mapsUrl,
    pageUrl,
  } = body;

  if (!owner || !type || !["location", "message"].includes(type)) {
    return json(400, { error: "Invalid payload" });
  }

  const emailSender = process.env.EMAIL_SENDER;
  const emailPassword = process.env.EMAIL_PASSWORD;
  const smtpServer = process.env.SMTP_SERVER;
  const smtpPort = Number(process.env.SMTP_PORT || 587);
  const telegramToken = process.env.TELEGRAM_BOT_TOKEN;

  const emailTarget = String(owner.owner_email || "").trim();
  const telegramTarget = String(owner.owner_telegram || "").trim();

  const results = {
    email: { sent: false, skipped: true },
    telegram: { sent: false, skipped: true },
  };

  const textForEmail = buildEmailText(type, owner, finderName, messageText, mapsUrl, pageUrl);
  const textForTelegram = buildTelegramText(type, owner, finderName, messageText, mapsUrl, pageUrl);

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
        subject: type === "location" ? `Lokasi baru untuk ${owner.item_name || "barang"}` : `Pesan baru untuk ${owner.item_name || "barang"}`,
        text: textForEmail,
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

  const success = Boolean(results.email.sent || results.telegram.sent);
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
