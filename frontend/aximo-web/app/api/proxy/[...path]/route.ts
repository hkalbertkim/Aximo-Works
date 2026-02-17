import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE =
  process.env.AXIMO_BACKEND_BASE ||
  "https://api.aximo.works"; // default for prod

function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`${name} is not set`);
  return v;
}

async function forward(req: NextRequest, pathParts: string[]) {
  const token = requireEnv("AXIMO_API_TOKEN");
  const url = new URL(req.url);

  // Preserve query string
  const target = `${BACKEND_BASE}/${pathParts.join("/")}${url.search}`;

  // Build headers (copy content-type etc.)
  const headers = new Headers(req.headers);
  headers.set("X-AXIMO-TOKEN", token);

  // Avoid leaking cookies/host related headers upstream
  headers.delete("cookie");
  headers.delete("host");

  const method = req.method.toUpperCase();

  const init: RequestInit = {
    method,
    headers,
    // body only for non-GET/HEAD
    body: method === "GET" || method === "HEAD" ? undefined : await req.text(),
    redirect: "manual",
  };

  const upstream = await fetch(target, init);

  // Pass-through status + body
  const respBody = await upstream.arrayBuffer();
  const respHeaders = new Headers(upstream.headers);

  // Ensure CORS is okay for same-origin calls (browser -> Next)
  // (Same-origin generally doesn’t need it, but harmless)
  respHeaders.set("Cache-Control", "no-store");

  return new NextResponse(respBody, {
    status: upstream.status,
    headers: respHeaders,
  });
}

type RouteContext = { params: Promise<{ path: string[] }> };

export async function GET(req: NextRequest, { params }: RouteContext) {
  const { path } = await params;
  return forward(req, path);
}
export async function POST(req: NextRequest, { params }: RouteContext) {
  const { path } = await params;
  return forward(req, path);
}
export async function PUT(req: NextRequest, { params }: RouteContext) {
  const { path } = await params;
  return forward(req, path);
}
export async function PATCH(req: NextRequest, { params }: RouteContext) {
  const { path } = await params;
  return forward(req, path);
}
export async function DELETE(req: NextRequest, { params }: RouteContext) {
  const { path } = await params;
  return forward(req, path);
}
