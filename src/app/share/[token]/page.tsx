import { notFound } from "next/navigation";
import { getNoteByShareToken } from "@/fixtures/notes";
import { ShareShell } from "@/features/share/share-shell";

export const dynamic = "force-dynamic";

export default async function SharePage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const note = getNoteByShareToken(token);
  if (!note) notFound();
  return <ShareShell note={note} />;
}
