import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  disconnectFacebook,
  getFacebookConnectUrl,
  getFacebookPages,
  getMyChannels,
  selectFacebookPage,
} from "@/features/channels/api/channelsApi";

export function useChannelsQuery() {
  return useQuery({
    queryKey: ["channels"],
    queryFn: getMyChannels,
  });
}

export function useFacebookPagesQuery(enabled: boolean) {
  return useQuery({
    queryKey: ["channels", "facebook", "pages"],
    queryFn: getFacebookPages,
    enabled,
  });
}

export function useConnectFacebookMutation() {
  return useMutation({
    mutationFn: getFacebookConnectUrl,
  });
}

export function useDisconnectFacebookMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: disconnectFacebook,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["channels"] });
      await queryClient.invalidateQueries({ queryKey: ["channels", "facebook", "pages"] });
    },
  });
}

export function useSelectFacebookPageMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: selectFacebookPage,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["channels"] });
      await queryClient.invalidateQueries({ queryKey: ["channels", "facebook", "pages"] });
    },
  });
}
