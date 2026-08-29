import { notFound, redirect } from "next/navigation";
import { ItemService, ShareService } from "@/server";
import { authEnabled } from "@/server";
import { getServerContext } from "@/app/api/_lib/http";
import { ReaderChrome } from "@/features/reader/reader-chrome";
import { itemToNote } from "@/lib/api";

export default async function ReadPage({
  params,
}: {
  params: Promise<{ itemId: string[] }>;
}) {
  const ctx = await getServerContext();
  if (authEnabled(ctx.root) && !ctx.user) redirect("/login");
  const { itemId } = await params;
  const id = itemId.map(decodeURIComponent).join("/");
  const items = new ItemService(ctx.settings);
  const item = items.getItem(id);
  if (!item) notFound();
  const html = items.readItemContent(id);
  const share = new ShareService(ctx.settings, ctx.root).activeShareForItem(id);
  const token = share ? String(share.url_path || "").split("/").filter(Boolean)[1] : undefined;
  return <ReaderChrome note={itemToNote(item, { html, shareToken: token })} html={html} interactiveEnabled={ctx.settings.shareInteractiveEnabled} />;
}
