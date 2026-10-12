// Intake endpoint for idea-test pages.
// Captures free-sample and paid-pilot form submissions, appends them to the
// Google Sheet tracker, and (optionally) emails a notification.
//
// Zero npm dependencies: uses Node's built-in crypto + global fetch (Node 18+).
//
// Required env vars (set in Vercel → Project → Settings → Environment Variables)
// before this does anything on go-live:
//   GOOGLE_SA_EMAIL      service-account email with edit access to the tracker
//   GOOGLE_SA_KEY        service-account private key (PEM; literal \n are handled)
//   TRACKER_SHEET_ID     spreadsheet id of "Idea Test Tracker"
// Optional:
//   INTAKE_RANGE         default "leadgen-1 intake!A:H"
//   RESEND_API_KEY       to email a notification
//   NOTIFY_EMAIL         where to send it (default sam@halsteadsystems.com)
//
// Until the Google env vars are set the function still returns 200 so the page
// confirms to the visitor; the submission is logged to the function console and
// an email is sent if RESEND is configured. Nothing is lost silently once wired.

function readBody(req) {
  return new Promise((resolve) => {
    let raw = "";
    req.on("data", (c) => (raw += c));
    req.on("end", () => {
      try {
        const ct = (req.headers["content-type"] || "").toLowerCase();
        if (ct.includes("application/json")) return resolve(JSON.parse(raw || "{}"));
        const params = new URLSearchParams(raw);
        const o = {};
        for (const [k, v] of params) o[k] = v;
        resolve(o);
      } catch (e) {
        resolve({});
      }
    });
  });
}

function b64url(buf) {
  return Buffer.from(buf).toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

async function googleAccessToken() {
  const email = process.env.GOOGLE_SA_EMAIL;
  let key = process.env.GOOGLE_SA_KEY;
  if (!email || !key) return null;
  key = key.replace(/\\n/g, "\n");
  const crypto = await import("node:crypto");
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = b64url(
    JSON.stringify({
      iss: email,
      scope: "https://www.googleapis.com/auth/spreadsheets",
      aud: "https://oauth2.googleapis.com/token",
      iat: now,
      exp: now + 3600,
    })
  );
  const signer = crypto.createSign("RSA-SHA256");
  signer.update(`${header}.${claim}`);
  const sig = b64url(signer.sign(key));
  const assertion = `${header}.${claim}.${sig}`;
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion,
    }),
  });
  if (!res.ok) throw new Error("token exchange failed: " + (await res.text()));
  return (await res.json()).access_token;
}

async function appendRow(row) {
  const sheetId = process.env.TRACKER_SHEET_ID;
  if (!sheetId) return false;
  const token = await googleAccessToken();
  if (!token) return false;
  const range = encodeURIComponent(process.env.INTAKE_RANGE || "leadgen-1 intake!A:H");
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/${range}:append?valueInputOption=USER_ENTERED`;
  const res = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ values: [row] }),
  });
  if (!res.ok) throw new Error("sheets append failed: " + (await res.text()));
  return true;
}

async function notify(sub) {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) return false;
  const to = process.env.NOTIFY_EMAIL || "sam@halsteadsystems.com";
  const lines = Object.entries(sub).map(([k, v]) => `${k}: ${v}`).join("\n");
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: "Halstead intake <intake@halsteadsystems.com>",
      to,
      subject: `New ${sub.kind || "intake"} — ${sub.website || sub.email || "lead"}`,
      text: lines,
    }),
  });
  return res.ok;
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ ok: false, error: "method_not_allowed" });
    return;
  }
  const data = await readBody(req);
  const sub = {
    ts: new Date().toISOString(),
    kind: data.kind || "sample",
    email: (data.email || "").slice(0, 200),
    website: (data.website || "").slice(0, 300),
    icp: (data.icp || "").slice(0, 2000),
    triggers: (data.triggers || "").slice(0, 2000),
    calendar: (data.calendar || "").slice(0, 300),
    source: (req.headers["referer"] || "").slice(0, 300),
  };

  // Always log, so a submission is recoverable from function logs even if a
  // downstream store is not yet wired.
  console.log("INTAKE", JSON.stringify(sub));

  const results = { logged: true, sheet: false, email: false };
  try {
    results.sheet = await appendRow([
      sub.ts, sub.kind, sub.email, sub.website, sub.icp, sub.triggers, sub.calendar, sub.source,
    ]);
  } catch (e) {
    console.error("sheet error", e.message);
  }
  try {
    results.email = await notify(sub);
  } catch (e) {
    console.error("email error", e.message);
  }

  res.status(200).json({ ok: true, stored: results });
}
