import { redirect } from "next/navigation";
import { authEnabled } from "@/server";
import { getServerContext } from "@/app/api/_lib/http";
import { WorkspaceView } from "@/features/workspace/workspace-view";

export default async function HomePage() {
  const ctx = await getServerContext();
  if (authEnabled(ctx.root) && !ctx.user) redirect("/login");
  return <WorkspaceView />;
}
