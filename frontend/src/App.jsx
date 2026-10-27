import AuthPage from "./components/auth/AuthPage.jsx";
import AppShell from "./components/layout/AppShell.jsx";
import Spinner from "./components/common/Spinner.jsx";
import { useAuth } from "./context/AuthContext.jsx";

export default function App() {
  const { status, user } = useAuth();
  if (status === "loading") {
    return <div className="flex h-full items-center justify-center"><Spinner className="h-8 w-8" /></div>;
  }
  if (status !== "authenticated") return <AuthPage />;
  return <AppShell key={user.id} />; // key: a different user always starts with fresh state
}
