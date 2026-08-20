import type { TFunction } from "i18next";

const defaultConfig = {
  theme: {
    colorPrimary: "#C0392B",
    darkMode: false,
    prefix: "hanbao",
    leftHeader: {
      logo: "",
      title: "Work with hanbao",
    },
    bubbleList: {
      userMessageAnchors: {
        variant: "navigator",
      },
    },
  },
  sender: {
    attachments: true,
    maxLength: 10000,
    longTextUpload: {
      enabled: true,
    },
    disclaimer: "Works for you, grows with you",
  },
  welcome: {
    greeting: "Hi, I'm hanbao.",
    description:
      "A smart companion by your side — I remember your days and preferences, chat with you, and can use tools to help.",
    avatar: "/online.svg",
    prompts: [
      {
        value: "Tell me about your day?",
      },
      {
        value: "What can I do for you?",
      },
    ],
  },
  api: {
    baseURL: "",
    token: "",
  },
} as const;

class ChatConfigProvider {
  getGreeting(t: TFunction): string {
    return t("chat.greeting");
  }

  getDescription(t: TFunction): string {
    return t("chat.description");
  }

  getPrompts(t: TFunction): Array<{ value: string }> {
    return [{ value: t("chat.prompt1") }, { value: t("chat.prompt2") }];
  }

  getConfig(t: TFunction) {
    return {
      ...defaultConfig,
      sender: {
        ...defaultConfig.sender,
        disclaimer: t("chat.disclaimer"),
      },
      welcome: {
        ...defaultConfig.welcome,
        greeting: this.getGreeting(t),
        description: this.getDescription(t),
        prompts: this.getPrompts(t),
      },
    };
  }
}

const configProvider = new ChatConfigProvider();

export function getDefaultConfig(t: TFunction) {
  return configProvider.getConfig(t);
}

export default defaultConfig;

export type DefaultConfig = typeof defaultConfig;

// Export provider for extension
export { configProvider };
