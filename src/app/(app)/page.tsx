import { redirect } from "next/navigation";
import { authEnabled, ItemService, NavigationConfigService, ShareService } from "@/server";
import { getServerContext } from "@/app/api/_lib/http";
import { WorkspaceView } from "@/features/workspace/workspace-view";

export default async function HomePage() {
  const ctx = await getServerContext();
  if (authEnabled(ctx.root) && !ctx.user) redirect("/login");
  const items = new ItemService(ctx.settings).publicManifest().items;
  const shares = new ShareService(ctx.settings, ctx.root)
    .listShares()
    .filter((row) => row.active)
    .map((row) => ({ item_id: String(row.item_id), url_path: String(row.url_path), active: Boolean(row.active) }));
  const navigation = new NavigationConfigService(ctx.settings).getConfig();
  return (
    <WorkspaceView
      initialItems={items}
      initialShares={shares}
      initialNav={navigation}
      initialInteractive={ctx.settings.shareInteractiveEnabled}
    />
  );
}
