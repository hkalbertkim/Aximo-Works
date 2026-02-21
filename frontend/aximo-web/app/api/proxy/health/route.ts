import { NextResponse } from "next/server";

const BACKEND_BASE = process.env.AXIMO_BACKEND_BASE || "https://api.aximo.works";

function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`${name} is not set`);
  return v;
}

function sanitize(text: string): string {
  return text.replace(/[\r\n\t]+/g, " ").replace(/[^\x20-\x7E]/g, "").trim().slice(0, 200);
}

export async function GET() {
  const ts = new Date().toISOString();
  let upstreamStatus: number | null = null;

  try {
    const token = requireEnv("AXIMO_API_TOKEN");
    const upstream = await fetch(`${BACKEND_BASE}/tasks`, {
      method: "GET",
      headers: {
        "X-AXIMO-TOKEN": token,
      },
      cache: "no-store",
      redirect: "manual",
    });
    upstreamStatus = upstream.status;

    if (upstream.ok) {
      return NextResponse.json(
        {
          ok: true,
          upstream_status: upstreamStatus,
          ts,
        },
        {
          status: 200,
          headers: { "Cache-Control": "no-store" },
        }
      );
    }

    const body = sanitize(await upstream.text());
    return NextResponse.json(
      {
        ok: false,
        upstream_status: upstreamStatus,
        error: body || `upstream returned HTTP ${upstreamStatus}`,
        hint: "Check Cloudflare Access session, AXIMO_API_TOKEN env, and backend /tasks health.",
      },
      {
        status: 502,
        headers: { "Cache-Control": "no-store" },
      }
    );
  } catch (e) {
    return NextResponse.json(
      {
        ok: false,
        upstream_status: upstreamStatus,
        error: sanitize(e instanceof Error ? e.message : "proxy health check failed"),
        hint: "Check Next runtime env (AXIMO_API_TOKEN / AXIMO_BACKEND_BASE) and backend reachability.",
      },
      {
        status: 500,
        headers: { "Cache-Control": "no-store" },
      }
    );
  }
}
