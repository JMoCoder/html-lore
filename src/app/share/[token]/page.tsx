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
  try {
    const root = await getRootSettings();
    const settings = settingsForShareToken(root, token);
    const payload = new ShareService(settings, root).publicReadByToken(token);
    return (
      <ShareShell
        title={payload.item.title}
        summary={payload.item.summary}
        html={payload.html}
        styles={payload.styles}
        mode={String(payload.share.mode || "safe")}
      />
    );
  } catch {
    notFound();
  }
}
