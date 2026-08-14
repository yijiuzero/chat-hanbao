export type SecurityScanErrorResponse = { type: 'security_scan_failed'; message: string };

export const getBlockedHistory = async () => ({ records: [] as any[], blocked: [] as any[] });
export const getSkillScanner = () => ({
  getBlockedHistory: async () => ({ records: [] as any[], blocked: [] as any[] }),
  rescan: async () => {},
});

export const securityApi = {
  getBlockedHistory,
  getSkillScanner,
};

// [hanbao] Skill scanner removed — stubs for API compatibility
