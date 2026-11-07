import { AuthForm } from "@/components/auth-form";
export default async function Login({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const params = await searchParams;
  return (
    <>
      {params.registered && (
        <p className="banner" role="status">
          Account created. Sign in to continue.
        </p>
      )}
      {params.reason === "expired" && (
        <p className="banner" role="status">
          Your session has ended. Please sign in again.
        </p>
      )}
      {params.reason === "updated" && (
        <p className="banner" role="status">
          Account updated. Sign in again with your new details.
        </p>
      )}
      {params.reason === "deleted" && (
        <p className="banner" role="status">
          Your account and associated data have been deleted.
        </p>
      )}
      <AuthForm />
    </>
  );
}
