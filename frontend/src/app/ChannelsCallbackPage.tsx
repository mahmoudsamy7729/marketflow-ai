import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

type CallbackStatus = "success" | "error";

interface ChannelCallbackMessage {
  code: string | null;
  message: string;
  provider: string;
  source: "channels-oauth-callback";
  status: CallbackStatus;
}

export function ChannelsCallbackPage() {
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const payload: ChannelCallbackMessage = {
      code: searchParams.get("code"),
      message: searchParams.get("message") ?? "Channel flow completed.",
      provider: searchParams.get("provider") ?? "facebook",
      source: "channels-oauth-callback",
      status: searchParams.get("status") === "error" ? "error" : "success",
    };

    if (window.opener && !window.opener.closed) {
      window.opener.postMessage(payload, window.location.origin);
    }

    const timeoutId = window.setTimeout(() => {
      window.close();
    }, 900);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [searchParams]);

  return (
    <main className="channels-callback-shell">
      <div className="channels-callback-card">
        <p className="dashboard-kicker">Channels callback</p>
        <h1>Finalizing connection...</h1>
        <p>
          This window will close automatically and refresh the channels page.
        </p>
      </div>
    </main>
  );
}
