import { notFound } from "next/navigation";
import { ShareService, settingsForShareToken } from "@/server";
import { getRootSettings } from "@/app/api/_lib/http";
import { ShareShell } from "@/features/share/share-shell";

export const dynamic = "force-dynamic";

export default async function SharePage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const payload = await readShare(token);
  if (!payload) notFound();
  return (
    <ShareShell
      title={payload.item.title}
      summary={payload.item.summary}
      html={payload.html}
      styles={payload.styles}
      mode={String(payload.share.mode || "safe")}
    />
  );
}

async function readShare(token: string) {
  try {
    const root = await getRootSettings();
    const settings = settingsForShareToken(root, token);
    return new ShareService(settings, root).publicReadByToken(token);
  } catch {
    return null;
  }
}
