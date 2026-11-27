import { AuthForm } from "./AuthForm";
import { Wordmark } from "./Wordmark";

export function AuthPage({ mode }: { mode: "signup" | "login" }) {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-5 sm:px-8">
      <header className="py-6">
        <Wordmark />
      </header>
      <main className="flex flex-1 items-start justify-center pb-16 pt-8 sm:pt-16">
        <AuthForm mode={mode} />
      </main>
    </div>
  );
}
