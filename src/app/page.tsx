import { notes } from "@/fixtures/notes";
import { WorkspaceView } from "@/features/workspace/workspace-view";

export default function HomePage() {
  return <WorkspaceView notes={notes} />;
}
