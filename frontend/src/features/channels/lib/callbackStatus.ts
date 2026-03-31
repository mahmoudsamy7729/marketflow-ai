import type { CallbackStatusBanner } from "@/features/channels/types/channels";

const errorMessages: Record<string, string> = {
  oauth_state_invalid: "The Facebook authorization request was invalid or no longer matches an active session.",
  oauth_state_expired: "The Facebook authorization request expired before it was completed.",
  oauth_state_consumed: "This Facebook authorization request has already been used.",
  facebook_configuration_error: "Facebook OAuth is not configured correctly on the backend.",
  facebook_token_exchange_failed: "Facebook token exchange failed. Try reconnecting.",
  facebook_profile_fetch_failed: "Facebook profile retrieval failed after authorization.",
};

export function getCallbackStatusBanner(
  provider: string | null,
  status: string | null,
  code: string | null,
): CallbackStatusBanner | null {
  if (provider !== "facebook" || !status) {
    return null;
  }

  if (status === "connected") {
    return {
      tone: "success",
      title: "Facebook connected",
      description: "The Facebook connection is active. Choose the page this workspace should publish to.",
    };
  }

  if (status === "error") {
    return {
      tone: "error",
      title: "Facebook connection failed",
      description:
        (code ? errorMessages[code] : null) ??
        "The Facebook authorization flow did not complete successfully.",
    };
  }

  return null;
}
