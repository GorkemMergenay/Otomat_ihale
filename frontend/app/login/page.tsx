import { LoginForm } from "@/components/LoginForm";

export const dynamic = "force-dynamic";

export default function LoginPage({
  searchParams,
}: {
  searchParams: Record<string, string | string[] | undefined>;
}) {
  const nextParam = searchParams.next;
  const nextPath = Array.isArray(nextParam) ? nextParam[0] : nextParam;

  return (
    <section className="login-page">
      <div className="login-panel">
        <LoginForm nextPath={nextPath || "/"} />
      </div>
    </section>
  );
}
