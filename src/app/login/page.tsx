import { redirect } from "next/navigation";
import { authEnabled } from "@/server";
import { getRootSettings } from "@/app/api/_lib/http";
import { LoginPanel } from "@/features/auth/login-panel";

export default async function LoginPage() {
  const settings = await getRootSettings();
  if (!authEnabled(settings)) redirect("/");
  return <LoginPanel />;
}
