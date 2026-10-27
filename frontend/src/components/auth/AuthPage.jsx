import { useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { HangerIcon } from "../common/icons.jsx";
import Spinner from "../common/Spinner.jsx";
import FormField from "./FormField.jsx";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(mode, f) {
  const errors = {};
  if (mode === "register" && !f.name.trim()) errors.name = "Name is required.";
  if (!EMAIL_RE.test(f.email.trim())) errors.email = "Enter a valid email address.";
  if (mode === "login") {
    if (!f.password) errors.password = "Password is required.";
  } else {
    if (f.password.length < 8) errors.password = "Use at least 8 characters.";
    else if (!/[A-Za-z]/.test(f.password) || !/\d/.test(f.password)) errors.password = "Include at least one letter and one number.";
    if (f.confirm !== f.password) errors.confirm = "Passwords do not match.";
  }
  return errors;
}

export default function AuthPage() {
  const { login, register, notice, clearNotice } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [info, setInfo] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const switchMode = (m) => {
    setMode(m);
    setErrors({});
    setFormError("");
    setInfo("");
    clearNotice();
  };

  async function onSubmit(e) {
    e.preventDefault();
    if (busy) return;
    const v = validate(mode, form);
    setErrors(v);
    setFormError("");
    if (Object.keys(v).length) return;

    setBusy(true);
    try {
      if (mode === "login") {
        await login(form.email.trim(), form.password);
      } else {
        await register({ name: form.name, email: form.email.trim(), password: form.password, confirm_password: form.confirm });
        setMode("login");
        setForm((f) => ({ ...f, password: "", confirm: "" }));
        setInfo("Account created. Please sign in.");
      }
    } catch (err) {
      const fields = {};
      for (const fe of err.fieldErrors) {
        const key = fe.field === "confirm_password" ? "confirm" : fe.field;
        if (key && ["name", "email", "password", "confirm"].includes(key)) fields[key] = fe.message;
      }
      setErrors(fields);
      setFormError(Object.keys(fields).length ? "" : err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-gradient-to-br from-brand-50 via-stone-50 to-brand-100 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-lg sm:p-8">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-brand-100 text-brand-700">
            <HangerIcon size={26} />
          </div>
          <h1 className="font-display text-2xl font-semibold text-stone-900">Fashion Styling Assistant</h1>
          <p className="mt-1 text-sm text-stone-500">Outfit and color advice grounded in a curated fashion knowledge base.</p>
        </div>

        <div className="mb-5 grid grid-cols-2 rounded-lg bg-stone-100 p-1 text-sm" role="tablist">
          {["login", "register"].map((m) => (
            <button
              key={m}
              role="tab"
              aria-selected={mode === m}
              onClick={() => switchMode(m)}
              className={`rounded-md py-1.5 font-medium transition ${mode === m ? "bg-white text-stone-900 shadow-sm" : "text-stone-500 hover:text-stone-700"}`}
            >
              {m === "login" ? "Sign in" : "Create account"}
            </button>
          ))}
        </div>

        {(notice || info) && (
          <p className="mb-4 rounded-lg bg-brand-50 px-3 py-2 text-sm text-brand-800" role="status">{info || notice}</p>
        )}
        {formError && <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{formError}</p>}

        <form onSubmit={onSubmit} noValidate className="space-y-4">
          {mode === "register" && (
            <FormField id="name" label="Full name" value={form.name} onChange={set("name")} error={errors.name} autoComplete="name" maxLength={80} />
          )}
          <FormField id="email" label="Email" type="email" value={form.email} onChange={set("email")} error={errors.email} autoComplete="email" />
          <FormField
            id="password" label="Password" type="password" value={form.password} onChange={set("password")} error={errors.password}
            autoComplete={mode === "login" ? "current-password" : "new-password"} maxLength={128}
          />
          {mode === "register" && (
            <FormField id="confirm" label="Confirm password" type="password" value={form.confirm} onChange={set("confirm")} error={errors.confirm} autoComplete="new-password" maxLength={128} />
          )}
          <button
            type="submit"
            disabled={busy}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
          >
            {busy && <Spinner className="h-4 w-4 !text-white" />}
            {mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}
