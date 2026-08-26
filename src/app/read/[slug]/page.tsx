import { notFound } from "next/navigation";
import { getNote } from "@/fixtures/notes";
import { ReaderChrome } from "@/features/reader/reader-chrome";

export default async function ReadPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const note = getNote(slug);
  if (!note) notFound();
  return <ReaderChrome note={note} />;
}
