# Custom Sign-In/Sign-Up Pages

## Basic Custom Pages

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <SignIn
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "bg-card shadow-lg",
          },
        }}
      />
    </div>
  );
}
```

```tsx
// app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <SignUp
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "bg-card shadow-lg",
          },
        }}
      />
    </div>
  );
}
```

## Theming with @clerk/themes

```bash
bun add @clerk/themes
```

```tsx
// app/layout.tsx
import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: "#8b5cf6",
          colorBackground: "#0a0a0a",
          colorInputBackground: "#1a1a1a",
          colorInputText: "#ffffff",
        },
        elements: {
          formButtonPrimary: "bg-primary hover:bg-primary/90",
          card: "bg-card border border-border",
          headerTitle: "text-foreground",
          headerSubtitle: "text-muted-foreground",
          socialButtonsBlockButton: "border-border",
          formFieldInput: "bg-input border-border",
          footerActionLink: "text-primary hover:text-primary/80",
        },
      }}
    >
      {children}
    </ClerkProvider>
  );
}
```

## Catppuccin Theme

```tsx
// lib/clerk-theme.ts
import { dark } from "@clerk/themes";

export const catppuccinTheme = {
  baseTheme: dark,
  variables: {
    // Mocha palette
    colorPrimary: "#cba6f7",      // Mauve
    colorBackground: "#1e1e2e",   // Base
    colorInputBackground: "#313244", // Surface0
    colorInputText: "#cdd6f4",    // Text
    colorText: "#cdd6f4",         // Text
    colorTextSecondary: "#a6adc8", // Subtext0
    colorDanger: "#f38ba8",       // Red
    colorSuccess: "#a6e3a1",      // Green
    colorWarning: "#f9e2af",      // Yellow
    borderRadius: "0.5rem",
  },
  elements: {
    card: "bg-[#1e1e2e] border border-[#313244]",
    headerTitle: "text-[#cdd6f4]",
    headerSubtitle: "text-[#a6adc8]",
    formButtonPrimary: "bg-[#cba6f7] hover:bg-[#cba6f7]/90 text-[#1e1e2e]",
    formFieldInput: "bg-[#313244] border-[#45475a] text-[#cdd6f4]",
    formFieldLabel: "text-[#cdd6f4]",
    footerActionLink: "text-[#cba6f7] hover:text-[#cba6f7]/80",
    identityPreviewEditButton: "text-[#cba6f7]",
    socialButtonsBlockButton: "border-[#45475a] text-[#cdd6f4]",
    dividerLine: "bg-[#45475a]",
    dividerText: "text-[#6c7086]",
  },
};
```

## Branded Sign-In Page

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from "@clerk/nextjs";
import Image from "next/image";

export default function SignInPage() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left: Branding */}
      <div className="hidden lg:flex flex-col justify-center p-12 bg-primary">
        <Image src="/logo-white.svg" alt="Logo" width={200} height={50} />
        <h1 className="mt-8 text-4xl font-bold text-white">
          Welcome back
        </h1>
        <p className="mt-4 text-white/80">
          Sign in to access your dashboard and manage your projects.
        </p>
      </div>

      {/* Right: Sign-in form */}
      <div className="flex items-center justify-center p-8">
        <SignIn
          appearance={{
            elements: {
              rootBox: "w-full max-w-md",
              card: "shadow-none p-0",
            },
          }}
        />
      </div>
    </div>
  );
}
```

## Custom UserButton Menu

```tsx
<UserButton afterSignOutUrl="/">
  <UserButton.MenuItems>
    <UserButton.Link
      label="Dashboard"
      href="/dashboard"
      labelIcon={<LayoutDashboard className="w-4 h-4" />}
    />
    <UserButton.Link
      label="Settings"
      href="/settings"
      labelIcon={<Settings className="w-4 h-4" />}
    />
    <UserButton.Action label="manageAccount" />
    <UserButton.Action label="signOut" />
  </UserButton.MenuItems>
</UserButton>
```
